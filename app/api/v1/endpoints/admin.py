"""
管理员相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.core.security import create_access_token
from app.services.admin import AsyncAdminService
from app.api.schemas.admin import AdminLoginRequest, AdminCreateRequest
from app.common.deps import get_current_admin
from app.models.admin import Admin

router = APIRouter()


@router.post("/login")
async def admin_login(
        request: AdminLoginRequest,
        db: AsyncSession = Depends(get_async_db)
):
    """
    管理员登录
    """
    try:
        service = AsyncAdminService(db)
        admin = await service.login(
            username=request.username,
            password=request.password
        )

        token_data = {"sub": admin["id"], "username": admin["username"], "role": admin["role"]}
        access_token = create_access_token(token_data)

        return {
            "code": 0,
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "admin": {
                    "id": admin["id"],
                    "username": admin["username"],
                    "real_name": admin["real_name"],
                    "role": admin["role"]
                }
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/create")
async def create_admin(
        request: AdminCreateRequest,
        current_admin: Admin = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_db)
):
    """
    创建管理员（仅超级管理员）
    """
    try:
        service = AsyncAdminService(db)
        admin = await service.create_admin(
            username=request.username,
            password=request.password,
            real_name=request.real_name,
            phone=request.phone,
            email=request.email,
            role=request.role
        )
        return {
            "code": 0,
            "message": "管理员创建成功",
            "data": {
                "id": admin.id,
                "username": admin.username,
                "role": admin.role
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def list_admins(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        current_admin: Admin = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取管理员列表
    """
    try:
        service = AsyncAdminService(db)
        result = await service.list_admins(page=page, page_size=page_size)
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logs")
async def get_admin_logs(
        admin_id: Optional[str] = Query(None, description="管理员ID"),
        action: Optional[str] = Query(None, description="操作类型"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        current_admin: Admin = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取操作日志
    """
    try:
        service = AsyncAdminService(db)
        result = await service.get_logs(
            admin_id=admin_id,
            action=action,
            page=page,
            page_size=page_size
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))