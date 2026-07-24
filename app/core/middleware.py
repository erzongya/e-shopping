# app/core/middleware.py
"""
中间件配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import List
import time
import uuid

from app.core.logger import log_info,log_error



class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 - 记录所有请求和响应"""

    async def dispatch(self, request: Request, call_next):
        # 1. 生成或获取 trace_id
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
        request.state.trace_id = trace_id

        # 2. 获取 session_id（从请求头或生成）
        session_id = request.headers.get("X-Session-ID", str(uuid.uuid4())[:8])
        request.state.session_id = session_id

        # 3. 记录请求开始
        start_time = time.time()
        log_info(
            trace_id,
            session_id,
            f"→ {request.method} {request.url.path}"
        )

        # 4. 处理请求
        try:
            response = await call_next(request)

            # 5. 记录响应
            process_time = time.time() - start_time
            log_info(
                trace_id,
                session_id,
                f"← {response.status_code} | 耗时: {process_time:.3f}s"
            )

            # 6. 添加响应头
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Session-ID"] = session_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 7. 记录异常
            process_time = time.time() - start_time
            log_error(
                trace_id,
                session_id,
                f"✗ 请求异常 | 耗时: {process_time:.3f}s | error: {str(e)}",
                e
            )
            raise


ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",  # 前端开发
    "http://localhost:8000",  # 后端开发
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]


def setup_middleware(app: FastAPI):
    """配置所有中间件"""

    # 1. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 请求日志
    app.add_middleware(RequestLogMiddleware)

    # 3. 可信主机（生产环境）
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=settings.ALLOWED_HOSTS
    # )