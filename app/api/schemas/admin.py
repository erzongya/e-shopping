# app/api/schemas/admin.py
"""
管理员相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== 请求模型 ====================

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")


class AdminCreateRequest(BaseModel):
    """创建管理员请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    role: str = Field("operator", description="角色: super_admin/admin/operator")


# ==================== 响应模型 ====================

class AdminInfoResponse(BaseModel):
    """管理员信息响应"""
    id: str
    username: str
    real_name: Optional[str]
    role: str
    status: int
    last_login_time: Optional[datetime]


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


class AdminLogResponse(BaseModel):
    """操作日志响应"""
    id: str
    admin_id: str
    action: str
    target: Optional[str]
    target_id: Optional[str]
    content: Optional[str]
    ip: Optional[str]
    created_at: datetime