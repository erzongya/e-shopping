from typing import TypedDict,Annotated,Sequence,Dict
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
# TypedDict 结构化字典类型定义
# Annotated  给类型附加额外备注 / 校验元数据 例：Annotated[int, "范围0-120", {"min":0, "max":120}]
# Sequence 通用有序可迭代序列（list/tuple/ 字符串）

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    goods_ids: list[str]
    goods_info: list[dict]
    too_call_round:int #记录工具调用次数


