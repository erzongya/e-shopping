"""
售后相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.services.aftersale import AsyncAfterSaleService
from app.api.schemas.aftersale import ApplyRefundRequest
from app.common.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/apply")
async def apply_refund(
        request: ApplyRefundRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    申请售后

    - 1: 仅退款
    - 2: 退货退款
    """
    try:
        service = AsyncAfterSaleService(db)
        result = await service.apply_refund(
            user_id=current_user.id,
            order_id=request.order_id,
            order_item_id=request.order_item_id,
            type=request.type,
            reason=request.reason,
            description=request.description,
            images=request.images
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{aftersale_id}")
async def get_aftersale_detail(
        aftersale_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取售后详情
    """
    try:
        service = AsyncAfterSaleService(db)
        result = await service.get_aftersale_detail(
            aftersale_id=aftersale_id,
            user_id=current_user.id
        )
        return {"code": 0, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def get_user_aftersales(
        status: Optional[int] = Query(None, description="状态筛选"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户售后列表
    """
    try:
        service = AsyncAfterSaleService(db)
        result = await service.get_user_aftersales(
            user_id=current_user.id,
            status=status,
            page=page,
            page_size=page_size
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))