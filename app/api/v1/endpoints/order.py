"""
订单相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.services.order import AsyncOrderService
from app.api.schemas.order import (
    CreateOrderRequest, PayOrderRequest, CancelOrderRequest
)
from app.common.deps import get_current_user
from app.models.user import User
from app.common.exceptions import NotFoundException

router = APIRouter()


@router.post("/create")
async def create_order(
        request: CreateOrderRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    创建订单

    - 从购物车选中商品创建订单
    - 需要选择收货地址
    """
    try:
        service = AsyncOrderService(db)
        result = await service.create_order(
            user_id=current_user.id,
            address_id=request.address_id,
            cart_ids=request.cart_ids,
            remark=request.remark
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/pay")
async def pay_order(
        order_id: str,
        request: PayOrderRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    支付订单

    - 支持余额支付
    """
    try:
        service = AsyncOrderService(db)
        result = await service.pay_order(
            order_id=order_id,
            user_id=current_user.id,
            pay_method=request.pay_method
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel")
async def cancel_order(
        order_id: str,
        request: CancelOrderRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    取消订单

    - 仅待支付状态可取消
    """
    try:
        service = AsyncOrderService(db)
        result = await service.cancel_order(
            order_id=order_id,
            user_id=current_user.id,
            reason=request.reason
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/confirm")
async def confirm_order(
        order_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    确认收货

    - 仅已发货状态可确认
    """
    try:
        service = AsyncOrderService(db)
        result = await service.confirm_order(
            order_id=order_id,
            user_id=current_user.id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}")
async def get_order_detail(
        order_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取订单详情
    """
    try:
        service = AsyncOrderService(db)
        result = await service.get_order_detail(
            order_id=order_id,
            user_id=current_user.id
        )
        return {"code": 0, "data": result}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def get_user_orders(
        status: Optional[int] = Query(None, description="订单状态筛选"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户订单列表
    """
    try:
        service = AsyncOrderService(db)
        result = await service.get_user_orders(
            user_id=current_user.id,
            status=status,
            page=page,
            page_size=page_size
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))