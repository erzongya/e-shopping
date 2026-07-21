from typing import List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import BaseTool

from agent.state import AgentState
from storage.redis_client import checkpointer
from common.llm_factory import get_chat_llm
from common.exception import BizErr, ErrCode
from common.logger import log_info

MAX_TOOL_CALL_ROUND: int = 2

SYSTEM_PROMPT = """你是专业电商业务智能助手，可完成商品查询、秒杀商品查看、用户订单查询、物流轨迹查询工作，所有业务数据必须依赖工具获取，禁止自己编造任何商品、订单、物流数据。
## 当前可用全部工具清单
1. query_user_order：查询订单，支持【user_id】/【order_no】二选一填写即可查询订单列表，status为可选过滤条件
2. query_logistics_track：根据快递tracking_no单号，查询整条物流流转轨迹
3. list_goods_by_filter：根据商品分类、关键词筛选商品列表
4. query_flash_goods：查询当前正在进行的秒杀商品列表
5. query_goods_detail：根据goods_id查询商品详情
6. check_goods_stock：校验商品库存数量

# 一、工具调用强制格式（严格贴合当前MCP解析规则，必须遵守）
1、统一tool_calls入参固定结构：args内部必须包裹一层kwargs字典，真实业务参数全部写在kwargs内层，格式标准示例：
正确标准写法：
{"name":"query_user_order","args":{"kwargs":{"order_no":"order_002"}}}
{"name":"query_user_order","args":{"kwargs":{"user_id":"user_001","status":"paid"}}}
{"name":"query_logistics_track","args":{"kwargs":{"tracking_no":"TK20260721001"}}}
{"name":"list_goods_by_filter","args":{"kwargs":{"category":"蓝牙耳机"}}}

2、禁止行为：
① 禁止直接把业务参数裸露放在args顶层，必须嵌套kwargs一层；
② 禁止混合自然文字+tool_calls一起输出，要调用工具时只返回标准tool_calls结构，不附加任何解释话术；
③ 禁止空工具名称、空参数、无效重复调用工具。

# 二、工具调用次数硬性约束
整个单次对话流程内，最多发起2次工具调用，到达2次调用上限后，无论工具返回结果如何，都停止继续调用工具，直接基于已获取的所有工具数据整理最终回答。

# 三、数据使用硬性规则
1、工具返回 isError=False、携带正常业务数据时：必须原样使用工具返回的真实数据库数据整理回答，绝对禁止使用自身知识库兜底编造商品、订单、物流信息。
2、工具返回 isError=True（执行异常/参数错误/无查询数据）：如实告知用户当前查询失败原因，仅可给出合理操作指引，不可编造数据补齐内容。
3、解析工具返回内容时，按照结构化格式清晰展示列表、订单、物流节点信息。

# 四、对话行为规范
1、用户明确给出订单号、商品分类、快递单号等关键字段，直接组装对应参数调用工具，不要主动向用户索要额外信息；
2、只有用户完全未提供任何查询条件时，才可引导用户补充对应关键字段；
3、工具返回空列表（无匹配数据），直白告知用户：当前未查询到对应记录，不要自行猜测补充数据。
"""


def create_agent_graph(tools: List[BaseTool], cp: BaseCheckpointSaver = checkpointer):
    llm = get_chat_llm()
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState) -> dict:
        messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        resp_msg = llm_with_tools.invoke(messages)
        log_info("", "system_agent_graph", f"LLM产生消息，是否携带工具调用: {bool(resp_msg.tool_calls)}")
        return {"messages": [resp_msg]}

    def update_round_node(state: AgentState) -> dict:
        # 打印全部消息栈，查看ToolMessage内容
        print("===== 所有消息 =====", state["messages"])
        current_round = state.get("tool_call_round", 0)
        new_round = current_round + 1
        log_info("", "system_agent_graph", f"工具执行完成，当前累计调用轮次: {new_round}")
        return {"tool_call_round": 1}

    def route_node(state: AgentState) -> str:
        current_round = state.get("tool_call_round", 0)
        msg_list = state.get("messages", [])
        if not msg_list:
            return END

        last_msg = msg_list[-1]
        # 内部拦截
        if current_round >= MAX_TOOL_CALL_ROUND:
            err_msg = f"工具调用已达到最大限制{MAX_TOOL_CALL_ROUND}轮，终止本次对话工具调用"
            log_info("", "system_agent_graph", err_msg)
            raise BizErr(code=ErrCode.MAX_TOOL_ROUND, msg="连续多次查询工具异常，暂时无法完成查询，请稍后重试")

        if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0:
            return "tools"
        return END

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", ToolNode(tools))
    graph_builder.add_node("update_round", update_round_node)

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges("agent", route_node, ["tools", END])
    graph_builder.add_edge("tools", "update_round")
    graph_builder.add_edge("update_round", "agent")

    # 保留你的checkpoint
    compiled_graph = graph_builder.compile(checkpointer=cp)
    return compiled_graph