from fastapi import FastAPI
import uvicorn
from common.middleware import TraceMiddleware
from common.exception import global_handler
from config.settings import settings
from api import chat_router
app = FastAPI(title='电商客服Agent接口')

# 注册中间件
app.add_middleware(TraceMiddleware)

# 绑定全局异常处理函数（核心一行）
app.add_exception_handler(Exception, global_handler)

# 挂载抽离后的对话路由
app.include_router(chat_router)
@app.get("/")
def index():
    return {"msg": "电商客服API服务运行中，请访问 /docs 调试接口"}
# 核心聊天接口实现
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )