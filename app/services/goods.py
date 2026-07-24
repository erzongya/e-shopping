# app/services/goods.py
"""
商品业务逻辑服务 - 异步版
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc, func
from datetime import datetime

from app.models.goods import Goods, GoodsSpec, GoodsComment, GoodsCategory
from app.common.exceptions import BusinessException, NotFoundException


class GoodsService:
    """商品业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_detail(self, goods_id: str) -> Dict[str, Any]:
        """
        获取商品详情

        Args:
            goods_id: 商品ID

        Returns:
            商品详情数据
        """
        # 查询商品
        result = await self.db.execute(
            select(Goods).where(
                Goods.id == goods_id,
                Goods.status == 1
            )
        )
        goods = result.scalar_one_or_none()

        if not goods:
            raise NotFoundException(f"商品不存在: {goods_id}")

        # 查询规格
        spec_result = await self.db.execute(
            select(GoodsSpec).where(GoodsSpec.goods_id == goods_id)
        )
        specs = spec_result.scalars().all()

        # 构建返回数据
        return {
            "id": goods.id,
            "name": goods.name,
            "category": goods.category,
            "sub_category": goods.sub_category,
            "brand": goods.brand,
            "price": float(goods.price),
            "flash_price": float(goods.flash_price) if goods.flash_price else 0.0,
            "stock": goods.stock,
            "sold_count": goods.sold_count,
            "desc": goods.desc,
            "images": goods.images,
            "is_flash": goods.is_flash,
            "flash_limit": goods.flash_limit,
            "buy_limit": goods.buy_limit,
            "flash_end_time": goods.flash_end_time.strftime("%Y-%m-%d %H:%M:%S") if goods.flash_end_time else None,
            "is_hot": goods.is_hot,
            "is_new": goods.is_new,
            "specs": [{
                "id": s.id,
                "spec_name": s.spec_name,
                "spec_value": s.spec_value,
                "spec_price": float(s.spec_price) if s.spec_price else 0.0,
                "spec_stock": s.spec_stock
            } for s in specs]
        }

    async def list_by_filter(
        self,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_flash: Optional[int] = None,
        is_hot: Optional[bool] = None,
        is_new: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        多条件筛选商品列表 - 异步
        """
        # 构建查询
        query = select(Goods).where(Goods.status == 1)

        # 应用筛选
        if category:
            query = query.where(Goods.category == category)
        if sub_category:
            query = query.where(Goods.sub_category == sub_category)
        if brand:
            query = query.where(Goods.brand == brand)
        if min_price is not None:
            query = query.where(Goods.price >= min_price)
        if max_price is not None:
            query = query.where(Goods.price <= max_price)
        if is_flash is not None:
            query = query.where(Goods.is_flash == is_flash)
        if is_hot is not None:
            query = query.where(Goods.is_hot == is_hot)
        if is_new is not None:
            query = query.where(Goods.is_new == is_new)
        if keyword:
            query = query.where(
                or_(
                    Goods.name.contains(keyword),
                    Goods.brand.contains(keyword)
                )
            )

        # 统计总数
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # 分页
        query = query.order_by(desc(Goods.created_at)).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        goods_list = result.scalars().all()

        # 构建返回数据
        items = [{
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "sub_category": g.sub_category,
            "brand": g.brand,
            "price": float(g.price),
            "flash_price": float(g.flash_price) if g.flash_price else 0.0,
            "stock": g.stock,
            "sold_count": g.sold_count,
            "is_flash": g.is_flash,
            "is_hot": g.is_hot,
            "is_new": g.is_new
        } for g in goods_list]

        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_flash_goods(self) -> List[Dict[str, Any]]:
        """获取正在进行的秒杀商品 - 异步"""
        now = datetime.now()

        result = await self.db.execute(
            select(Goods).where(
                Goods.is_flash == 1,
                Goods.flash_end_time > now,
                Goods.stock > 0,
                Goods.status == 1
            )
        )
        goods_list = result.scalars().all()

        return [{
            "id": g.id,
            "name": g.name,
            "flash_price": float(g.flash_price),
            "stock": g.stock,
            "flash_limit": g.flash_limit,
            "flash_end_time": g.flash_end_time.strftime("%Y-%m-%d %H:%M:%S") if g.flash_end_time else None
        } for g in goods_list]

    async def get_specs(self, goods_id: str) -> List[Dict[str, Any]]:
        """获取商品规格 - 异步"""
        # 检查商品是否存在
        goods_result = await self.db.execute(
            select(Goods).where(Goods.id == goods_id)
        )
        goods = goods_result.scalar_one_or_none()

        if not goods:
            raise NotFoundException(f"商品不存在: {goods_id}")

        spec_result = await self.db.execute(
            select(GoodsSpec).where(GoodsSpec.goods_id == goods_id)
        )
        specs = spec_result.scalars().all()

        return [{
            "spec_id": s.id,
            "spec_name": s.spec_name,
            "spec_value": s.spec_value,
            "spec_price": float(s.spec_price) if s.spec_price else 0.0,
            "spec_stock": s.spec_stock
        } for s in specs]

    async def get_comments(
        self,
        goods_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取商品评论 - 异步"""
        # 检查商品是否存在
        goods_result = await self.db.execute(
            select(Goods).where(Goods.id == goods_id)
        )
        goods = goods_result.scalar_one_or_none()

        if not goods:
            raise NotFoundException(f"商品不存在: {goods_id}")

        # 查询评论
        query = select(GoodsComment).where(
            GoodsComment.goods_id == goods_id,
            GoodsComment.status == 1
        )

        # 统计总数
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # 分页
        query = query.order_by(desc(GoodsComment.created_at)).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        comments = result.scalars().all()

        comment_list = [{
            "id": c.id,
            "content": c.content,
            "score": c.score,
            "tag": c.tag,
            "images": c.images,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None
        } for c in comments]

        return {
            "comment_list": comment_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def get_categories(self, parent_id: str = "0") -> List[Dict[str, Any]]:
        """获取商品分类 - 异步"""
        result = await self.db.execute(
            select(GoodsCategory)
            .where(GoodsCategory.parent_id == parent_id)
            .order_by(desc(GoodsCategory.sort))
        )
        categories = result.scalars().all()

        return [{
            "id": c.id,
            "name": c.name,
            "level": c.level,
            "icon": c.icon,
            "children": await self.get_categories(c.id) if c.level < 3 else []
        } for c in categories]