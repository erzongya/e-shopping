"""
购物车业务逻辑服务 - 异步版
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.models.goods import Goods, GoodsSpec
from app.common.exceptions import BusinessException, NotFoundException
from app.models.cart import Cart


class AsyncCartService:
    """购物车业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_to_cart(
        self,
        user_id: str,
        goods_id: str,
        quantity: int = 1,
        spec_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加商品到购物车"""
        # 1. 检查商品是否存在
        result = await self.db.execute(
            select(Goods).where(
                Goods.id == goods_id,
                Goods.status == 1
            )
        )
        goods = result.scalar_one_or_none()
        if not goods:
            raise NotFoundException("商品不存在或已下架")

        # 2. 检查库存
        if goods.stock < quantity:
            raise BusinessException(f"库存不足，当前库存: {goods.stock}")

        # 3. 检查是否已在购物车中
        result = await self.db.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.goods_id == goods_id,
                Cart.spec_id == spec_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.quantity += quantity
            await self.db.commit()
            await self.db.refresh(existing)
            return {"id": existing.id, "quantity": existing.quantity}

        # 4. 新增购物车
        cart = Cart(
            user_id=user_id,
            goods_id=goods_id,
            spec_id=spec_id,
            quantity=quantity
        )
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)

        return {"id": cart.id, "quantity": cart.quantity}

    async def update_quantity(self, cart_id: str, user_id: str, quantity: int) -> Dict[str, Any]:
        """更新购物车数量"""
        if quantity <= 0:
            return await self.remove_from_cart(cart_id, user_id)

        result = await self.db.execute(
            select(Cart).where(
                Cart.id == cart_id,
                Cart.user_id == user_id
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            raise NotFoundException("购物车商品不存在")

        # 检查库存
        result = await self.db.execute(
            select(Goods).where(Goods.id == cart.goods_id)
        )
        goods = result.scalar_one_or_none()
        if goods and goods.stock < quantity:
            raise BusinessException(f"库存不足，当前库存: {goods.stock}")

        cart.quantity = quantity
        await self.db.commit()
        await self.db.refresh(cart)

        return {"id": cart.id, "quantity": cart.quantity}

    async def remove_from_cart(self, cart_id: str, user_id: str) -> Dict[str, Any]:
        """从购物车移除商品"""
        result = await self.db.execute(
            select(Cart).where(
                Cart.id == cart_id,
                Cart.user_id == user_id
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            raise NotFoundException("购物车商品不存在")

        await self.db.delete(cart)
        await self.db.commit()

        return {"id": cart_id, "removed": True}

    async def toggle_select(self, cart_id: str, user_id: str) -> Dict[str, Any]:
        """切换购物车选中状态"""
        result = await self.db.execute(
            select(Cart).where(
                Cart.id == cart_id,
                Cart.user_id == user_id
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            raise NotFoundException("购物车商品不存在")

        cart.selected = not cart.selected
        await self.db.commit()
        await self.db.refresh(cart)

        return {"id": cart.id, "selected": cart.selected}

    async def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """清空购物车"""
        result = await self.db.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        carts = result.scalars().all()

        for cart in carts:
            await self.db.delete(cart)

        await self.db.commit()

        return {"cleared": True, "count": len(carts)}

    async def get_cart_list(self, user_id: str) -> Dict[str, Any]:
        """获取购物车列表"""
        result = await self.db.execute(
            select(Cart).where(Cart.user_id == user_id).order_by(desc(Cart.created_at))
        )
        carts = result.scalars().all()

        total_amount = 0
        selected_amount = 0
        cart_list = []

        for cart in carts:
            # 查询商品信息
            result = await self.db.execute(
                select(Goods).where(Goods.id == cart.goods_id)
            )
            goods = result.scalar_one_or_none()
            price = 0
            stock = 0
            goods_name = "商品已下架"
            goods_image = None

            if goods:
                goods_name = goods.name
                goods_image = goods.images.split(",")[0] if goods.images else None
                stock = goods.stock
                price = float(goods.flash_price) if goods.is_flash == 1 and goods.flash_price > 0 else float(goods.price)

            # 查询规格
            spec_name = None
            if cart.spec_id and goods:
                result = await self.db.execute(
                    select(GoodsSpec).where(GoodsSpec.id == cart.spec_id)
                )
                spec = result.scalar_one_or_none()
                if spec:
                    spec_name = spec.spec_name
                    price += float(spec.spec_price) if spec.spec_price else 0

            item_total = price * cart.quantity
            total_amount += item_total
            if cart.selected:
                selected_amount += item_total

            cart_list.append({
                "id": cart.id,
                "goods_id": cart.goods_id,
                "goods_name": goods_name,
                "goods_image": goods_image,
                "spec_id": cart.spec_id,
                "spec_name": spec_name,
                "price": price,
                "quantity": cart.quantity,
                "total": item_total,
                "stock": stock,
                "selected": cart.selected
            })

        return {
            "list": cart_list,
            "total_count": len(cart_list),
            "total_amount": total_amount,
            "selected_amount": selected_amount
        }