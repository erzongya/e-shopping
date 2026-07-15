from fastapi import FastAPI
import uvicorn
from config.settings import settings
from common.middleware import TraceMiddleware
from common.exception import global_handler
from api import chat_router
from mcp_server.mcp_client import mcp_manager
import asyncio
from agent.graph import create_agent_graph
from contextlib import asynccontextmanager

# 全局缓存graph实例
agent_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_graph
    print("【服务启动】预加载全部资源")
    try:
        # 顺序预加载
        tools = await mcp_manager.initialize()
        # 构建graph
        agent_graph = create_agent_graph(tools=tools)
        print("【完成】MCP+Graph全部就绪")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"启动预加载失败：{e}")
        # 不强制退出，本地调试会走懒加载兜底
    yield
    print("服务关闭")

# 初始化主应用
app = FastAPI(lifespan=lifespan)

# 1. 注册全局中间件
app.add_middleware(TraceMiddleware)
# 2. 全局统一异常捕获
app.add_exception_handler(Exception, global_handler)



# 3. 挂载业务路由
app.include_router(chat_router)

# 核心聊天接口实现
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )