from fastapi import Request
from fastapi.responses import JSONResponse
from common.logger import log_error


# 业务错误码
class ErrCode:
    PARAM = 40001
    LLM = 50001
    DB = 50002

class BizErr(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg

# 全局异常捕获
async def global_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    session_id = request.headers.get("X-Session-Id", "")

    if isinstance(exc, BizErr):
        log_error(trace_id, session_id, f"业务异常:{exc.msg}")
        return JSONResponse({"code": exc.code, "msg": exc.msg, "data": None})
    else:
        log_error(trace_id, session_id, f"系统异常:{str(exc)}")
        return JSONResponse({"code": 99999, "msg": "服务异常，请稍后重试", "data": None}, status_code=500)
