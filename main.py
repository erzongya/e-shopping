from fastapi import FastAPI
import uvicorn

from common.middleware import TraceMiddleware
from common.exception import global_handler
from common.logger import log_info, log_error
from api import chat_router
# 修正：和之前完整MCP客户端文件路径匹配 mcp_server/client/manager.py
from mcp_server.client.manager import mcp_manager
from agent.graph import create_agent_graph
from contextlib import asynccontextmanager

from config.settings import settings
from agent.context import set_agent_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    trace_id = ""
    sys_sid = "system_fastapi_main"
    log_info(trace_id, sys_sid, "FastAPI服务启动，开始预加载资源")
    try:
        tools = await mcp_manager.initialize()
        graph = create_agent_graph(tools=tools)
        # 存入上下文，不再暴露全局变量给外部导入
        set_agent_graph(graph)
        log_info(trace_id, sys_sid, "MCP+Agent Graph预加载全部完成，服务就绪")
    except Exception as e:
        log_error(trace_id, sys_sid, "服务启动预加载资源失败", e)
        raise RuntimeError("启动失败") from e
    yield
    log_info(trace_id, sys_sid, "FastAPI服务正常关闭，释放资源")

# 初始化FastAPI主应用，绑定生命周期
app = FastAPI(
    title="电商智能客服Agent服务",
    description="基于LangGraph+分布式MCP微服务的电商对话智能体",
    lifespan=lifespan,
    version="1.0.0"
)

# 1. 注册全链路追踪中间件
app.add_middleware(TraceMiddleware)
# 2. 全局统一异常处理器（业务异常/系统异常统一返回格式）
app.add_exception_handler(Exception, global_handler)

# 3. 挂载对话业务路由
app.include_router(chat_router)


if __name__ == '__main__':
    # 区分环境：开发环境reload=True，生产固定False
    dev_reload = True if settings.ENV == "dev" else False
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=dev_reload
    )