# agent/context.py
from typing import Optional
from langgraph.graph import StateGraph

# 全局存储Agent实例
_agent_graph: Optional[StateGraph] = None

def set_agent_graph(graph: StateGraph) -> None:
    """服务启动时写入graph实例"""
    global _agent_graph
    _agent_graph = graph

def get_agent_graph() -> Optional[StateGraph]:
    """所有接口统一读取graph"""
    return _agent_graph