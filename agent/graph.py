from common.llm_factory import get_chat_llm
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.tools import search_similar_goods, get_goods_detail,query_order, check_return_eligibility,filter_goods
from storage.redis_client import checkpointer

# 系统提示词
SYSTEM_PROMPT = """
你是企业电商智能客服，所有输出严格依赖工具查询数据，禁止编造。
## 商品业务
1. 用户查商品先调用search_similar_goods，再get_goods_detail；有预算/库存要求必须调用filter_goods过滤。
2. 无匹配商品统一回复：暂无符合条件的商品。商品用表格输出。
## 订单售后
1. 查询订单调用query_order，退货校验调用check_return_eligibility，明确告知能否退货。
## 约束
回答简洁，不拓展无关内容，无工具调用直接结束对话。
"""


# 1 记载大模型
llm = get_chat_llm()
# 2 绑定工具
# 统一包装，再放进工具数组
tools = [
    search_similar_goods,get_goods_detail,query_order,check_return_eligibility,filter_goods
]

llm_with_tools = llm.bind_tools(tools)
# 3 构建流程图
def agent_think(state:AgentState):
    if not state["messages"]:
        return state
    full_msg = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    resp = llm_with_tools.invoke(full_msg)
    return {"messages": [resp]}
# 路由判断
def route_node(state: AgentState):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0:
        return "tools"
    return END
# 构建图
builder = StateGraph(AgentState)
builder.add_node("agent", agent_think)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route_node, ["tools", END])
builder.add_edge("tools", "agent")

# 挂载RedisSaver，自动持久化会话快照
graph = builder.compile(checkpointer=checkpointer)