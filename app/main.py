# app/main.py
"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.core.logger import log_info, log_error
from app.core.middleware import setup_middleware
from app.common.exceptions import register_exception_handlers
from app.core.settings import settings
from app.api.v1.router import api_router
from app.core.database import init_db, async_engine
from app.core.redis import redis_client
from app.agent.manager import agent_manager
from app.retrieval.vector_store import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理"""
    log_info("", "lifespan", "🚀 服务启动...")

    try:
        await init_db()
        log_info("", "lifespan", "✅ 数据库初始化完成")

        await redis_client.connect()
        log_info("", "lifespan", "✅ Redis 连接成功")

        await agent_manager.initialize()
        log_info("", "lifespan", f"✅ Agent 初始化完成，工具数: {len(agent_manager._tools)}")

        chunk_count = vector_store.load_documents()
        log_info("", "lifespan", f"✅ RAG 加载完成，共 {chunk_count} 个块")

        app.state.is_ready = True
        log_info("", "lifespan", "🎉 服务启动完成")



        yield

        await async_engine.dispose()
        await redis_client.close()
        log_info("", "lifespan", "✅ 资源释放完成")

    except Exception as e:
        log_error("", "lifespan", "❌ 启动失败", e)
        raise


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

setup_middleware(app)
register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "agent": agent_manager.is_ready()}


@app.get("/ready")
async def ready():
    if not getattr(app.state, "is_ready", False) or not agent_manager.is_ready():
        return {"status": "not ready"}, 503
    return {"status": "ready"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )