# app/api/v1/endpoints/user.py
"""
用户相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.user import AsyncUserService
from app.api.schemas.user import UpdateNicknameRequest, AddressRequest
from app.common.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取当前用户信息"""
    service = AsyncUserService(db)
    data = await service.get_profile(current_user.id)
    return {"code": 0, "message": "success", "data": data}


@router.put("/me/nickname")
async def update_nickname(
    request: UpdateNicknameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """更新用户昵称"""
    service = AsyncUserService(db)
    user = await service.update_nickname(current_user.id, request.nickname)
    return {
        "code": 0,
        "message": "昵称更新成功",
        "data": {"nickname": user.nickname}
    }


@router.get("/me/addresses")
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取用户收货地址列表"""
    service = AsyncUserService(db)
    data = await service.get_addresses(current_user.id)
    return {"code": 0, "message": "success", "data": data}


@router.post("/me/addresses")
async def add_address(
    request: AddressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """添加收货地址"""
    service = AsyncUserService(db)
    address = await service.add_address(
        user_id=current_user.id,
        name=request.name,
        phone=request.phone,
        province=request.province,
        city=request.city,
        district=request.district,
        address=request.address,
        is_default=request.is_default
    )
    return {"code": 0, "message": "地址添加成功", "data": address}


@router.delete("/me/addresses/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """删除收货地址"""
    service = AsyncUserService(db)
    await service.delete_address(current_user.id, address_id)
    return {"code": 0, "message": "地址删除成功"}


@router.put("/me/addresses/{address_id}/default")
async def set_default_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """设置默认地址"""
    service = AsyncUserService(db)
    await service.set_default_address(current_user.id, address_id)
    return {"code": 0, "message": "默认地址设置成功"}


@router.get("/me/points")
async def get_points(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取用户积分"""
    service = AsyncUserService(db)
    points = await service.get_points(current_user.id)
    return {
        "code": 0,
        "message": "success",
        "data": {"user_id": current_user.id, "points": points}
    }