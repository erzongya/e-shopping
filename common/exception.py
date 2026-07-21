from fastapi import Request
from fastapi.responses import JSONResponse
from common.logger import log_error
import traceback

# 业务错误码统一枚举（全局唯一标准）
class ErrCode:
    # 参数类 4xxxx
    PARAM_ERROR = 40001
    TOOL_ARGS_ERROR = 40002
    MAX_TOOL_ROUND = 40003
    # 服务不可用 5xxxx
    LLM_ERR = 50001
    DB_ERR = 50002
    MCP_CONNECT_FAIL = 50003
    SERVICE_UNAVAILABLE = 50004
    # 未知系统异常
    SYSTEM_ERR = 99999

# 业务自定义异常
class BizErr(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(msg)

# 统一成功返回封装，全项目接口复用
def success_json(data, trace_id: str = None):
    return JSONResponse({
        "code": 0,
        "msg": "success",
        "data": data,
        "trace_id": trace_id or ""
    })

# 全局统一异常处理器（挂载到app.add_exception_handler）
async def global_handler(request: Request, exc: Exception):
    # 从链路中间件获取追踪ID
    trace_id = getattr(request.state, "trace_id", "unknown")
    # 从请求头拿会话ID
    session_id = request.headers.get("X-Session-Id", "")

    # 业务自定义异常：仅打印信息，无堆栈
    if isinstance(exc, BizErr):
        log_error(trace_id, session_id, f"【业务异常】code={exc.code} msg={exc.msg}")
        return JSONResponse({
            "code": exc.code,
            "msg": exc.msg,
            "data": None,
            "trace_id": trace_id
        })

    # 底层系统未知异常：打印完整堆栈日志
    err_msg = f"【系统未知异常】{str(exc)}"
    log_error(trace_id, session_id, err_msg, exc)
    return JSONResponse(
        content={
            "code": ErrCode.SYSTEM_ERR,
            "msg": "服务异常，请稍后重试",
            "data": None,
            "trace_id": trace_id
        },
        status_code=500
    )