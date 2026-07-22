from typing import TypedDict, List, Optional,Annotated,Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent状态定义 - 对标LangGraph标准"""

    # 原有字段（保留）
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: Optional[str]


    tool_records: List[dict]  # 所有工具调用记录
    error_info: Optional[str]  # 错误信息
    call_count: int  # 工具调用计数
    retry_count: int  # 重试次数
    max_retries: int  # 最大重试次数
    max_tool_calls: int  # 最大工具调用次数

    # 路由相关
    next_action: Optional[Literal["tool", "finish", "error_retry", "manual", "rag"]]
    final_answer: Optional[str]  # 最终回答

    # rag
    rag_context: Optional[str]  # RAG检索到的文档