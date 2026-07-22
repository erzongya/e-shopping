# agent/graph.py
from typing import List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from agent.state import AgentState
from common.llm_factory import get_chat_llm
from common.logger import log_info
from agent.prompts import build_system_prompt

MAX_TOOL_CALL_ROUND: int = 2


def create_agent_graph(tools: List[BaseTool], cp: BaseCheckpointSaver):
    llm = get_chat_llm()
    llm_with_tools = llm.bind_tools(tools)

    # ===================== 节点定义 =====================
    def agent_node(state: AgentState) -> dict:
        """Agent节点 - 使用动态Prompt"""
        messages = state["messages"]

        # 动态生成System Prompt
        last_msg = messages[-1] if messages else None
        user_query = last_msg.content if last_msg else ""
        system_prompt = build_system_prompt(user_query)

        # 构造完整消息
        full_messages = [SystemMessage(content=system_prompt)] + messages
        resp_msg = llm_with_tools.invoke(full_messages)

        log_info("", "system_agent_graph", f"LLM返回，是否有tool_calls: {bool(resp_msg.tool_calls)}")

        return {"messages": [resp_msg]}

    # ===================== 路由函数 =====================
    def route_after_agent(state: AgentState) -> str:
        """LLM输出完成后的路由分支"""
        last_msg = state["messages"][-1]
        has_tool_call = hasattr(last_msg, "tool_calls") and len(last_msg.tool_calls) > 0
        current_cnt = state.get("call_count", 0)

        # 达到最大调用次数，直接结束
        if has_tool_call and current_cnt >= MAX_TOOL_CALL_ROUND:
            log_info("", "system_agent_graph", f"已到达工具调用上限{MAX_TOOL_CALL_ROUND}轮，终止工具调用")
            return END

        if has_tool_call:
            return "tools"

        return END

    # ===================== 组装Graph =====================
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", ToolNode(tools))

    # 入口
    graph_builder.add_edge(START, "agent")

    # agent → 条件路由
    graph_builder.add_conditional_edges(
        source="agent",
        path=route_after_agent,
        path_map={
            "tools": "tools",
            END: END
        }
    )

    graph_builder.add_edge("tools", "agent")

    # 编译
    compiled_graph = graph_builder.compile(checkpointer=cp)
    return compiled_graph