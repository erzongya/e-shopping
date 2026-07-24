
from pydantic import BaseModel, Field, validator
from typing import Optional
import re


# ==================== 请求模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class RegisterRequest(BaseModel):
    """注册请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含数字')
        if not any(char.isupper() for char in v):
            raise ValueError('密码必须包含大写字母')
        return v


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str = Field(..., description="刷新Token")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=20, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")

    @validator('new_password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含数字')
        if not any(char.isupper() for char in v):
            raise ValueError('密码必须包含大写字母')
        return v


# ==================== 响应模型 ====================

class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: str
    nickname: str
    phone: str
    vip_level: int
    point: int
    is_vip: bool = False


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


class TokenResponse(BaseModel):
    """Token刷新响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None