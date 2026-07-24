"""
运营相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.ops import AsyncOpsService
from app.common.deps import get_current_admin
from app.models.admin import Admin

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取运营仪表盘数据
    """
    try:
        service = AsyncOpsService(db)
        data = await service.get_dashboard_stats()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales-report")
async def get_sales_report(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取销售报表
    """
    try:
        service = AsyncOpsService(db)
        data = await service.get_sales_report(start_date, end_date)
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user-stats")
async def get_user_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户统计数据
    """
    try:
        service = AsyncOpsService(db)
        data = await service.get_user_stats()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goods-stats")
async def get_goods_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取商品统计数据
    """
    try:
        service = AsyncOpsService(db)
        data = await service.get_goods_stats()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-stats")
async def get_order_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取订单统计数据
    """
    try:
        service = AsyncOpsService(db)
        data = await service.get_order_stats()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))