from fastapi import Request
from fastapi.responses import JSONResponse
from common.logger import log_error


# 业务错误码
class ErrCode:
    PARAM = 40001
    LLM = 50001
    DB = 50002
    # 新增Agent/MCP专属错误
    MCP_CONNECT_FAIL = 50003  # MCP服务连接失败
    TOOL_ARGS_ERROR = 40002  # 工具参数解析错误
    MAX_TOOL_ROUND = 40003  # 达到最大工具调用轮次，终止对话
class BizErr(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg

# 成功统一返回函数（和异常返回结构对齐）
def success_json(data, trace_id: str = None):
    return JSONResponse({
        "code": 0,
        "msg": "success",
        "data": data,
        "trace_id": trace_id
    })

# 全局异常捕获（保留你原有逻辑，仅微调日志输出）
async def global_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    session_id = request.headers.get("X-Session-Id", "")

    if isinstance(exc, BizErr):
        log_error(trace_id, session_id, f"业务异常:{exc.msg}")
        return JSONResponse({
            "code": exc.code,
            "msg": exc.msg,
            "data": None,
            "trace_id": trace_id
        })
    else:
        log_error(trace_id, session_id, f"系统异常:{str(exc)}")
        return JSONResponse({
            "code": 99999,
            "msg": "服务异常，请稍后重试",
            "data": None,
            "trace_id": trace_id
        }, status_code=500)