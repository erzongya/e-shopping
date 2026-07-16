from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from agent.state import AgentState
from storage.redis_client import checkpointer
from common.llm_factory import get_chat_llm
from langchain_core.messages import SystemMessage
from common.exception import BizErr, ErrCode


# 最大允许工具调用轮次
MAX_TOOL_CALL_ROUND = 2
def create_agent_graph(tools):
    # 系统提示词
    sys_prompt = """你是一个电商物流助手，负责处理电商物流相关的任务。
    # 工具调用强制规范（必须严格遵守）
    1. 优先使用平台原生结构化 tool_calls 输出工具调用，严禁把工具调用JSON写入普通回复content文本内；
    2. 参数规则：所有参数平铺在args顶层，禁止任何嵌套、外层包装、kwargs包裹；
    3. 标准格式示例：
    {"name":"search_similar_goods","args":{"keyword":"蓝牙耳机","top_k":3}}
    {"name":"query_order","args":{"order_no":"OD20260716"}}
    4. 禁止无效调用：不得输出工具名空、参数为空的工具调用；
    5. 参数范围限制：仅使用工具Schema中定义的顶层字段，不新增多余参数、不嵌套参数；

    ## 兼容兜底规则（仅平台无原生函数调用时生效）
    1. 只能单独输出一行纯工具调用JSON，前后不能附带任何解释、对话文字；
    2. 禁止自然回答与工具调用JSON混合输出，二者不可同时存在；
    3. 全程保持参数平铺，不使用任何嵌套包裹结构。
    """

    def agent_node(state: AgentState):
        llm = get_chat_llm()
        bind_llm = llm.bind_tools(tools)
        messages = [SystemMessage(content=sys_prompt)]+ state["messages"]
        resp = bind_llm.invoke(messages)
        print("LLM输出工具调用：", resp)
        return {"messages": [resp]}

    # 更新工具迭代次数
    def update_round_node(state: AgentState):
        current = state.get("tool_call_round", 0)
        return {"tool_call_round": current + 1}

    # 路由根据工具调用次数判断是否调用工具或结束对话
    def route_node(state: AgentState):
        round_cnt = state.get("tool_call_round", 0)
        last_msg = state["messages"][-1]

        # 达到最大调用次数，抛出业务异常，由全局异常处理器捕获
        if round_cnt >= MAX_TOOL_CALL_ROUND:
            raise BizErr(
                code=ErrCode.MAX_TOOL_ROUND,
                msg="连续多次查询工具异常，暂时无法完成查询，请稍后重试"
            )

        if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0:
            return "tools"
        return END

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("update_round", update_round_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_node, ["tools", END])
    builder.add_edge("tools", "update_round")
    builder.add_edge("update_round", "agent")
    return builder.compile(checkpointer=checkpointer)
