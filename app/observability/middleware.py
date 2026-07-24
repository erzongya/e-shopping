import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.metrics import metrics
from app.core.logger import log_info, log_error


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
       可观测性中间件

       自动记录每个请求的：
           - 请求路径
           - 响应状态码
           - 处理耗时

       特别针对 /chat 接口：
           还会记录 LLM 调用次数和工具调用次数
    """

    async def dispatch(self, request: Request, call_next):
        """
        中间件核心方法

        执行流程：
            1. 请求进来 → 记录开始
            2. 执行实际业务 → await call_next(request)
            3. 响应返回 → 记录结束
        """
        # -------- 1. 请求开始 --------
        session_id = request.headers.get("X-Session-Id", f"session_{int(time.time())}")
        user_id = request.headers.get("X-User-Id", "anonymous")

        # 如果是 /chat 接口，开始记录对话
        if request.url.path == "/chat":
            metrics.start_conversation(session_id, user_id)

        # -------- 2. 执行业务逻辑 --------
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # -------- 3. 记录成功 --------
            # 如果是 /chat 接口，结束对话并记录统计
            if request.url.path == "/chat":
                stats = metrics.end_conversation(status="success")
                if stats:
                    log_info("", session_id,
                             f"对话完成: LLM={stats.llm_call_count}次, "
                             f"工具={stats.tool_call_count}次, "
                             f"token={stats.total_tokens}, "
                             f"耗时={stats.total_duration_ms:.0f}ms"
                             )

            # 添加响应头（方便调试）
            response.headers["X-Duration-Ms"] = str(round(duration_ms, 2))
            return response

        except Exception as e:
            # -------- 4. 记录失败 --------
            duration_ms = (time.time() - start_time) * 1000

            if request.url.path == "/chat":
                metrics.end_conversation(status="error", error_info=str(e))

            log_error("", session_id, f"请求失败: {e}", e)
            raise