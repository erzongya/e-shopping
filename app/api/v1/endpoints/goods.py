# app/api/v1/endpoints/goods.py
"""
商品相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.services.goods import GoodsService
from app.common.exceptions import NotFoundException

router = APIRouter()


@router.get("/detail/{goods_id}")
async def get_goods_detail(
    goods_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取商品详情"""
    try:
        service = GoodsService(db)
        data = await service.get_detail(goods_id)
        return {"code": 0, "data": data}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def list_goods(
    category: Optional[str] = Query(None, description="商品分类"),
    sub_category: Optional[str] = Query(None, description="子分类"),
    brand: Optional[str] = Query(None, description="品牌"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    is_flash: Optional[int] = Query(None, description="是否秒杀: 1是 0否"),
    is_hot: Optional[bool] = Query(None, description="是否热卖"),
    is_new: Optional[bool] = Query(None, description="是否新品"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """商品列表筛选"""
    try:
        service = GoodsService(db)
        result = await service.list_by_filter(
            category=category,
            sub_category=sub_category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            is_flash=is_flash,
            is_hot=is_hot,
            is_new=is_new,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/flash")
async def get_flash_goods(
    db: AsyncSession = Depends(get_async_db)
):
    """获取秒杀商品列表"""
    try:
        service = GoodsService(db)
        data = await service.get_flash_goods()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/spec/{goods_id}")
async def get_goods_spec(
    goods_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取商品规格"""
    try:
        service = GoodsService(db)
        data = await service.get_specs(goods_id)
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/comment/{goods_id}")
async def get_goods_comments(
    goods_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取商品评论"""
    try:
        service = GoodsService(db)
        result = await service.get_comments(goods_id, page, page_size)
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories")
async def get_categories(
    parent_id: str = Query("0", description="父分类ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """获取商品分类"""
    try:
        service = GoodsService(db)
        data = await service.get_categories(parent_id)
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))