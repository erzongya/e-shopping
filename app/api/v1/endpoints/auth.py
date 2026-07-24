from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_async_db
from app.core.security import create_access_token, create_refresh_token
from app.services.user import AsyncUserService

router = APIRouter()


class LoginRequest(BaseModel):
    phone: str
    password: str


class RegisterRequest(BaseModel):
    phone: str
    password: str
    nickname: str
    email: Optional[str] = None
    avatar: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(
        request: LoginRequest,
        db: AsyncSession = Depends(get_async_db)
):
    """
    用户登录
    - 支持手机号登录
    - 返回 access_token 和 refresh_token
    """
    try:
        service = AsyncUserService(db)
        user = await service.login(
            phone=request.phone,
            password=request.password
        )

        token_data = {"sub": user.id, "phone": user.phone}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "code": 0,
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user_info": {
                    "id": user.id,
                    "nickname": user.nickname,
                    "phone": user.phone,
                    "vip_level": user.vip_level,
                    "point": user.point
                }
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/register")
async def register(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_async_db)
):
    """
    用户注册
    - 手机号注册
    - 返回用户信息
    """
    try:
        service = AsyncUserService(db)
        user = await service.register(
            phone=request.phone,
            password=request.password,
            nickname=request.nickname,
            email=request.email,
            avatar=request.avatar
        )

        return {
            "code": 0,
            "message": "注册成功",
            "data": {
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "email": user.email,
                "avatar": user.avatar,
                "vip_level": user.vip_level,
                "point": user.point
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh_token(
        request: RefreshTokenRequest,
        db: AsyncSession = Depends(get_async_db)
):
    """
    刷新 access_token
    - 使用 refresh_token 换取新的 access_token
    """
    try:
        # 验证 refresh_token
        from app.core.security import decode_token
        payload = decode_token(request.refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="无效的 refresh_token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的 refresh_token")

        service = AsyncUserService(db)
        user = await service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        token_data = {"sub": user.id, "phone": user.phone}
        new_access_token = create_access_token(token_data)

        return {
            "code": 0,
            "message": "刷新成功",
            "data": {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(
        db: AsyncSession = Depends(get_async_db)
):
    """
    用户登出
    - 暂不实现 token 黑名单
    """
    return {
        "code": 0,
        "message": "登出成功"
    }


@router.get("/me")
async def get_current_user(
        db: AsyncSession = Depends(get_async_db),
        # current_user: User = Depends(get_current_user)  # 需要实现 get_current_user 依赖
):
    """
    获取当前用户信息
    """
    # 这个接口需要先实现 get_current_user 依赖
    return {
        "code": 0,
        "message": "获取用户信息成功",
        "data": None
    }