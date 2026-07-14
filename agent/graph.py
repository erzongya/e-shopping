from utils.llm_factory import get_chat_llm
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.tools import search_similar_goods, get_goods_detail,query_order, check_return_eligibility,filter_goods


SYSTEM_PROMPT = """
你是企业官方电商智能客服，所有回复仅采信工具查询的商品、订单真实数据，严禁虚构任何信息。
## 商品咨询
1. 用户检索商品，必须先调用search_similar_goods获取ID，再调用get_goods_detail查完整商品列表。
2. 用户说明预算、想要有货商品时，拿到商品列表后必须调用filter_goods过滤。
3. 仅还原原始商品参数，禁止自行新增卖点、使用场景。
4. 过滤后无匹配商品统一话术：暂无符合您预算/库存要求的商品。
5. 商品信息采用表格标准化输出。
## 订单&售后
1. 订单、退货业务必须调取数据库，清晰展示订单号、状态、实付金额。
2. 受理退货前先核验售后资格，不符合需明确告知拒绝理由。
## 服务要求
沟通礼貌简洁，不随意拓展无关内容，不主观推演。
"""


# 1 记载大模型
llm = get_chat_llm()
# 2 绑定工具
tools = [search_similar_goods, get_goods_detail, query_order, check_return_eligibility,filter_goods]
llm_with_tools = llm.bind_tools(tools)
# 3 构建流程图
def agent_think(state:AgentState):
    messages = state["messages"]
    if not messages:
        return {"messages": []}
    full_msg = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(full_msg)
    return {"messages": [response]}

tool_node = ToolNode(tools)

def business_route(state:AgentState):
    last_msg = state["messages"][-1]
    #判断是否存在工具调用
    if hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0:
        return 'tools'
    return  END
builder = StateGraph(AgentState)
builder.add_node("agent", agent_think)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
# 路由：模型需要调用工具则走tools，否则直接结束
builder.add_conditional_edges("agent", business_route,['tools',END])

builder.add_edge("tools", "agent")
builder.add_edge("agent", END)

# 编译图
graph = builder.compile()