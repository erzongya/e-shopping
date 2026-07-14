import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from langchain_core.tools import StructuredTool

# 链路追踪中间件
class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        resp = await call_next(request)
        resp.headers["X-Trace-Id"] = trace_id
        return resp



def wrap_safe_tool(fn):
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return f"工具异常：{str(e)}"
    # 原生工具构建，不破坏签名
    return StructuredTool.from_function(inner)