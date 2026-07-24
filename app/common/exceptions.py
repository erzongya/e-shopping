"""
自定义异常定义 + 全局异常处理器
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Optional
from app.core.settings import settings


# ========== 自定义异常 ==========

class AppException(Exception):
    """应用基础异常"""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data


class NotFoundException(AppException):
    """资源不存在 - 404"""

    def __init__(self, resource: str, identifier: str = ""):
        super().__init__(
            code=404,
            message=f"{resource}不存在",
            data={"resource": resource, "id": identifier}
        )


class BusinessException(AppException):
    """业务异常 - 400"""

    def __init__(self, message: str, data: Any = None):
        super().__init__(code=400, message=message, data=data)


class UnauthorizedException(AppException):
    """未授权 - 401"""

    def __init__(self, message: str = "请先登录"):
        super().__init__(code=401, message=message)


class PermissionDeniedException(AppException):
    """权限不足 - 403"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(code=403, message=message)


class ValidationException(AppException):
    """参数校验失败 - 422"""

    def __init__(self, message: str, data: Any = None):
        super().__init__(code=422, message=message, data=data)


# ========== 异常码定义 ==========

class ErrorCode:
    """错误码常量"""
    # 通用
    SUCCESS = 0
    SYSTEM_ERROR = 9999

    # 认证 (1000-1099)
    UNAUTHORIZED = 1001
    TOKEN_EXPIRED = 1002
    INVALID_TOKEN = 1003
    PERMISSION_DENIED = 1004

    # 用户 (1100-1199)
    USER_NOT_FOUND = 1101
    USER_EXISTS = 1102
    PASSWORD_ERROR = 1103
    USER_FROZEN = 1104

    # 商品 (1200-1299)
    GOODS_NOT_FOUND = 1201
    GOODS_OUT_OF_STOCK = 1202
    GOODS_OFF_SALE = 1203

    # 订单 (1300-1399)
    ORDER_NOT_FOUND = 1301
    ORDER_STATUS_ERROR = 1302
    ORDER_PAY_ERROR = 1303


# ========== 全局异常处理器 ==========

def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """应用自定义异常"""
        return JSONResponse(
            status_code=exc.code if exc.code < 600 else 400,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局兜底异常"""
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.SYSTEM_ERROR,
                "message": "服务器内部错误",
                "data": {"detail": str(exc)} if settings.DEBUG else None
            }
        )