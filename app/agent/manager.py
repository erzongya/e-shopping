# app/agent/manager.py
"""
Agent 管理器
"""
import redis.asyncio as redis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.memory import MemorySaver
from app.agent.graph import create_agent_graph
from app.mcp_server.manager import mcp_manager
from app.core.logger import log_info, log_error
from app.core.settings import settings


class AgentManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._graph = None
        self._tools = []
        self._is_ready = False

    async def initialize(self):
        if self._is_ready:
            return

        log_info("", "agent", "🚀 初始化 Agent...")

        self._tools = await mcp_manager.initialize()
        log_info("", "agent", f"✅ 加载 {len(self._tools)} 个工具")

        # ✅ 异步 Redis Checkpointer
        try:
            async with AsyncRedisSaver.from_conn_string(settings.REDIS_URL) as checkpointer:
                await checkpointer.asetup()
                self._graph = create_agent_graph(self._tools, checkpointer)
                log_info("", "agent", "✅ Redis Checkpointer 连接成功")
        except Exception as e:
            checkpointer = MemorySaver()
            log_error("", "agent", f"⚠️ 降级到内存存储: {e}")

        self._graph = create_agent_graph(self._tools, checkpointer)
        self._is_ready = True
        log_info("", "agent", "✅ Agent 初始化完成")

    def get_graph(self):
        if not self._is_ready:
            raise RuntimeError("Agent 未初始化")
        return self._graph

    def is_ready(self):
        return self._is_ready


agent_manager = AgentManager()