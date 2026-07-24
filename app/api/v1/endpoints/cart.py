"""
购物车相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.cart import AsyncCartService
from app.api.schemas.cart import AddToCartRequest, UpdateCartRequest
from app.common.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/add")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    添加到购物车
    """
    try:
        service = AsyncCartService(db)
        result = await service.add_to_cart(
            user_id=current_user.id,
            goods_id=request.goods_id,
            quantity=request.quantity,
            spec_id=request.spec_id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cart_id}")
async def update_cart(
    cart_id: str,
    request: UpdateCartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新购物车数量
    """
    try:
        service = AsyncCartService(db)
        result = await service.update_quantity(
            cart_id=cart_id,
            user_id=current_user.id,
            quantity=request.quantity
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}")
async def remove_from_cart(
    cart_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    从购物车移除商品
    """
    try:
        service = AsyncCartService(db)
        result = await service.remove_from_cart(
            cart_id=cart_id,
            user_id=current_user.id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/toggle")
async def toggle_select(
    cart_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    切换商品选中状态
    """
    try:
        service = AsyncCartService(db)
        result = await service.toggle_select(
            cart_id=cart_id,
            user_id=current_user.id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    清空购物车
    """
    try:
        service = AsyncCartService(db)
        result = await service.clear_cart(user_id=current_user.id)
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def get_cart_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取购物车列表
    """
    try:
        service = AsyncCartService(db)
        result = await service.get_cart_list(user_id=current_user.id)
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))