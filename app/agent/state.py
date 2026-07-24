from typing import TypedDict, List, Optional,Annotated,Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent状态定义 - 对标LangGraph标准"""

    # 原有字段（保留）
    messages: Annotated[List[BaseMessage], add_messages]
    call_count: int
    user_id: Optional[str]
    session_id: Optional[str]
    current_query: Optional[str]