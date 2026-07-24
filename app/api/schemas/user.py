# app/api/schemas/user.py
"""
用户相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


# ==================== 请求模型 ====================

class UpdateNicknameRequest(BaseModel):
    """更新昵称请求"""
    nickname: str = Field(..., min_length=1, max_length=50, description="新昵称")


class AddressRequest(BaseModel):
    """添加地址请求"""
    name: str = Field(..., min_length=2, max_length=50, description="收货人姓名")
    phone: str = Field(..., description="收货人手机号")
    province: str = Field(..., max_length=50, description="省份")
    city: str = Field(..., max_length=50, description="城市")
    district: str = Field(..., max_length=50, description="区县")
    address: str = Field(..., max_length=500, description="详细地址")
    is_default: bool = Field(False, description="是否默认地址")

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


# ==================== 响应模型 ====================

class AddressResponse(BaseModel):
    """地址响应"""
    id: str
    name: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    is_default: bool


class UserProfileResponse(BaseModel):
    """用户信息响应"""
    id: str
    nickname: str
    phone: str
    avatar: Optional[str]
    vip_level: int
    point: int
    total_spent: float
    register_time: str


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None