from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from agent.state import AgentState
from storage.redis_client import checkpointer
from common.llm_factory import get_chat_llm
from langchain_core.messages import SystemMessage
def create_agent_graph(tools):
    # 系统提示词
    sys_prompt = """
    你是企业电商智能客服，所有输出严格依赖工具查询数据，禁止编造。
    ## 工具调用强制格式约束
    1. 调用search_similar_goods时，参数直接写 {"keyword": "关键词"}，绝对不要用kwargs包裹。
    2. 连续2次调用工具失败，直接告知用户系统异常，停止重复调用工具。
    ## 商品业务
    1. 用户查商品先调用search_similar_goods，再get_goods_detail；有预算/库存要求必须调用filter_goods过滤。
    2. 无匹配商品统一回复：暂无符合条件的商品。商品用表格输出。
    ## 订单售后
    1. 查询订单调用query_order，退货校验调用check_return_eligibility，明确告知能否退货。
    ## 约束
    回答简洁，不拓展无关内容，无工具调用直接结束对话。
    """

    def agent_node(state: AgentState):
        llm = get_chat_llm()
        bind_llm = llm.bind_tools(tools)
        messages = [SystemMessage(content=sys_prompt)]+ state["messages"]
        resp = bind_llm.invoke(messages)
        print("LLM输出工具调用：", resp)
        return {"messages": [resp]}

    def route_node(state: AgentState):
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls):
            return "tools"
        return END

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_node, ["tools", END])
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=checkpointer)
