from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from common.middleware import TraceMiddleware
from common.exception import global_handler
from common.logger import log_info, log_error
from api import chat_router
from mcp_server.client.manager import mcp_manager
from agent.graph import create_agent_graph
from config.settings import settings
from agent.context import set_agent_graph
from langgraph.checkpoint.redis import AsyncRedisSaver
from retrieval.vector_store import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    trace_id = ""
    sys_sid = "system_fastapi_main"
    log_info(trace_id, sys_sid, "FastAPI服务启动，开始预加载资源")

    try:
        redis_url = "redis://127.0.0.1:6379/0"

        async with AsyncRedisSaver.from_conn_string(redis_url) as redis_saver:
            # 1 redis 连接初始化
            await redis_saver.setup()
            log_info(trace_id, sys_sid, "Redis Checkpoint 连接成功")

            # 2 加载 MCP 工具
            mcp_tools = await mcp_manager.initialize()
            log_info(trace_id, sys_sid, f"MCP 工具加载完成，共 {len(mcp_tools)} 个工具")

            # 3 创建 Agent Graph
            agent_graph = create_agent_graph(tools=mcp_tools, cp=redis_saver)
            set_agent_graph(agent_graph)
            log_info(trace_id, sys_sid, "Agent Graph 创建成功")

            # 🆕 4. 初始化 RAG
            log_info(trace_id, sys_sid, "开始加载 RAG 知识库...")
            chunk_count = vector_store.load_documents()
            log_info(trace_id, sys_sid, f"RAG 知识库加载完成，共 {chunk_count} 个块")

            log_info(trace_id, sys_sid, "🎉 服务启动完成，所有资源就绪")

            # yield 让服务运行（在 async with 块内部）
            yield

            log_info(trace_id, sys_sid, "FastAPI服务正常关闭，释放资源")
            # 退出 async with 块时自动清理 Redis 连接

    except Exception as e:
        log_error(trace_id, sys_sid, "服务启动预加载资源失败", e)
        raise RuntimeError("启动失败") from e


app = FastAPI(
    title="电商智能客服Agent服务",
    description="基于LangGraph+分布式MCP微服务的电商对话智能体",
    lifespan=lifespan,
    version="1.0.0"
)

app.add_middleware(TraceMiddleware)
app.add_exception_handler(Exception, global_handler)
app.include_router(chat_router)

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )