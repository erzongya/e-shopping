"""
促销相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.services.promotion import AsyncPromotionService
from app.api.schemas.promotion import ReceiveCouponRequest, CalculateDiscountRequest
from app.common.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/current")
async def get_current_promotions(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取当前有效的促销活动
    """
    try:
        service = AsyncPromotionService(db)
        data = await service.get_current_promotions()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate")
async def calculate_discount(
    request: CalculateDiscountRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    计算促销优惠
    """
    try:
        service = AsyncPromotionService(db)
        result = await service.calculate_discount(
            amount=request.amount,
            promotion_id=request.promotion_id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/coupons")
async def get_coupons(
    status: int = Query(1, description="状态: 1有效 2已停用"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取可领取的优惠券列表
    """
    try:
        service = AsyncPromotionService(db)
        data = await service.get_coupons(status=status)
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/coupons/receive")
async def receive_coupon(
    request: ReceiveCouponRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    领取优惠券
    """
    try:
        service = AsyncPromotionService(db)
        result = await service.receive_coupon(
            user_id=current_user.id,
            coupon_id=request.coupon_id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user-coupons")
async def get_user_coupons(
    status: Optional[int] = Query(None, description="状态: 1未使用 2已使用 3已过期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户已领取的优惠券
    """
    try:
        service = AsyncPromotionService(db)
        data = await service.get_user_coupons(
            user_id=current_user.id,
            status=status
        )
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))