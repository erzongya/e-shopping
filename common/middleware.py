import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from langchain_core.tools import StructuredTool
# 导入日志
from common.logger import log_info
# 链路追踪中间件
class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成全链路唯一trace_id挂载到request.state
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        sid = request.headers.get("X-Session-Id", "unknown")
        log_info(trace_id, sid, f"收到HTTP请求，路径：{request.url.path}")
        resp = await call_next(request)
        log_info(trace_id, sid, f"请求处理完成，响应状态码：{resp.status_code}")
        return resp


# def wrap_safe_tool(fn: object) -> object:
#     def inner(*args, **kwargs):
#         try:
#             return fn(*args, **kwargs)
#         except Exception as e:
#             return f"工具异常：{str(e)}"
#     # 原生工具构建，不破坏签名
#     return StructuredTool.from_function(inner)