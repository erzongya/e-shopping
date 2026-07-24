# agent/graph.py
from typing import List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from app.agent.state import AgentState
from app.common.llm_factory import get_chat_llm
from app.core.logger import log_info
from app.agent.prompts import build_system_prompt
# from app.observability import metrics
import time
MAX_TOOL_CALL_ROUND: int = 2


def create_agent_graph(tools: List[BaseTool], cp: BaseCheckpointSaver):
    llm = get_chat_llm().bind_tools(tools)

    # ===================== 节点定义 =====================
    async def agent_node(state: AgentState) -> dict:
        """Agent节点 - 使用动态Prompt"""
        messages = state.get("messages", [])
        user_query = state.get("current_query", "")

        system_prompt = build_system_prompt(user_query)
        full_messages = [SystemMessage(content=system_prompt)] + list(messages)


        start = time.time()
        reponse = await llm.ainvoke(full_messages)
        # duration_ms = (time.time() - start) * 1000
        # # 提取 token
        # input_tokens = 0
        # output_tokens = 0
        # if hasattr(reponse, "usage_metadata"):
        #     input_tokens = reponse.usage_metadata.get("input_tokens", 0)
        #     output_tokens = reponse.usage_metadata.get("output_tokens", 0)
        # elif hasattr(reponse, "response_metadata"):
        #     usage = reponse.response_metadata.get("token_usage", {})
        #     input_tokens = usage.get("prompt_tokens", 0)
        #     output_tokens = usage.get("completion_tokens", 0)
        # metrics.record_llm_call(
        #     model="gpt-4",
        #     input_tokens=input_tokens,
        #     output_tokens=output_tokens,
        #     duration_ms=duration_ms,
        #     has_tool_calls=bool(reponse.tool_calls)
        # )
        log_info("", "agent", f"工具调用: {reponse.tool_calls}")
        return {"messages": [reponse]}

    # ===================== 路由函数 =====================
    def route(state: AgentState) -> str:
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
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    compiled = builder.compile(checkpointer=cp)
    return compiled