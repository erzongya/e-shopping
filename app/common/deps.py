# app/common/deps.py
"""
依赖注入
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_async_db
from app.core.security import decode_token
from app.services.user import AsyncUserService
from app.models.user import User
from typing import Optional

# ==================== HTTP Bearer 认证 ====================

security = HTTPBearer()


# ==================== 获取当前用户 ====================

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_async_db)
) -> User:
    """
    从请求头获取当前登录用户

    使用方式：
        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Returns:
        User: 当前登录的用户对象

    Raises:
        HTTPException: Token无效或用户不存在
    """
    token = credentials.credentials

    # 1. 解码 Token
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token缺少用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 查询用户
    service = AsyncUserService(db)
    user = await service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被冻结或删除",
        )

    return user


# ==================== 获取当前活跃用户 ====================

async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户（已登录且状态正常）
    """
    if current_user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被冻结或删除",
        )
    return current_user


# ==================== 获取当前管理员 ====================

async def get_current_admin(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员（需要有管理员权限）
    """
    # 检查是否为管理员（根据你的业务逻辑调整）
    # 方式1: 用户有 role 字段
    if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


# ==================== 获取当前超级管理员 ====================

async def get_current_super_admin(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前超级管理员
    """
    if not hasattr(current_user, 'role') or current_user.role != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )
    return current_user


# ==================== 可选当前用户（允许未登录） ====================

async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_async_db)
) -> Optional[User]:
    """
    获取当前用户（允许未登录）

    使用方式：
        @router.get("/profile")
        async def get_profile(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                return {"user_id": current_user.id}
            return {"message": "未登录"}
    """
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        return None

    if not user_id:
        return None

    service = AsyncUserService(db)
    user = await service.get_user_by_id(user_id)

    return user