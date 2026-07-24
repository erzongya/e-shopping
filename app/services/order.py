"""
订单业务逻辑服务 - 异步版
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from datetime import datetime
import random

from app.models.order import Order, OrderItem, OrderLog
from app.models.cart import Cart
from app.models.goods import Goods, GoodsSpec
from app.models.user import User, UserAddress
from app.common.exceptions import BusinessException, NotFoundException
from app.common.enums import OrderStatus


class AsyncOrderService:
    """订单业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_order_no(self) -> str:
        """生成订单号 格式: 年月日 + 8位随机数"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        random_str = str(random.randint(10000000, 99999999))
        return f"{date_str}{random_str}"

    async def create_order(
        self,
        user_id: str,
        address_id: str,
        cart_ids: List[str],
        remark: str = ""
    ) -> Dict[str, Any]:
        """创建订单"""
        # 1. 获取收货地址
        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()
        if not address:
            raise NotFoundException("收货地址不存在")

        # 2. 获取购物车商品
        result = await self.db.execute(
            select(Cart).where(
                Cart.id.in_(cart_ids),
                Cart.user_id == user_id,
                Cart.selected == True
            )
        )
        carts = result.scalars().all()

        if not carts:
            raise BusinessException("购物车为空或未选中任何商品")

        # 3. 计算订单金额并检查库存
        total_amount = 0
        order_items = []

        for cart in carts:
            result = await self.db.execute(
                select(Goods).where(Goods.id == cart.goods_id)
            )
            goods = result.scalar_one_or_none()
            if not goods:
                raise BusinessException(f"商品不存在: {cart.goods_id}")

            if goods.stock < cart.quantity:
                raise BusinessException(f"商品 {goods.name} 库存不足")

            price = float(goods.flash_price) if goods.is_flash == 1 and goods.flash_price > 0 else float(goods.price)

            spec = None
            if cart.spec_id:
                result = await self.db.execute(
                    select(GoodsSpec).where(GoodsSpec.id == cart.spec_id)
                )
                spec = result.scalar_one_or_none()
                if spec:
                    price += float(spec.spec_price) if spec.spec_price else 0

            item_amount = price * cart.quantity
            total_amount += item_amount

            order_items.append({
                "goods_id": cart.goods_id,
                "spec_id": cart.spec_id,
                "goods_name": goods.name,
                "goods_image": goods.images.split(",")[0] if goods.images else None,
                "spec_name": spec.spec_name if cart.spec_id and spec else None,
                "price": price,
                "quantity": cart.quantity,
                "total_amount": item_amount
            })

        # 4. 计算运费（满99包邮）
        freight_amount = 0.00 if total_amount >= 99 else 10.00
        pay_amount = total_amount + freight_amount

        # 5. 生成订单号
        order_no = self.generate_order_no()

        # 6. 创建订单
        order = Order(
            order_no=order_no,
            user_id=user_id,
            total_amount=total_amount,
            discount_amount=0.00,
            freight_amount=freight_amount,
            pay_amount=pay_amount,
            status=OrderStatus.PENDING.value,
            receiver_name=address.name,
            receiver_phone=address.phone,
            receiver_province=address.province,
            receiver_city=address.city,
            receiver_district=address.district,
            receiver_address=address.address,
            user_remark=remark
        )

        self.db.add(order)
        await self.db.flush()

        # 7. 创建订单明细
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                goods_id=item["goods_id"],
                spec_id=item["spec_id"],
                goods_name=item["goods_name"],
                goods_image=item["goods_image"],
                spec_name=item["spec_name"],
                price=item["price"],
                quantity=item["quantity"],
                total_amount=item["total_amount"]
            )
            self.db.add(order_item)

        # 8. 记录订单日志
        log = OrderLog(
            order_id=order.id,
            operator=user_id,
            action="create",
            content="创建订单",
            after_status=OrderStatus.PENDING.value
        )
        self.db.add(log)

        # 9. 删除购物车
        for cart in carts:
            await self.db.delete(cart)

        # 10. 减少商品库存
        for cart in carts:
            result = await self.db.execute(
                select(Goods).where(Goods.id == cart.goods_id)
            )
            goods = result.scalar_one_or_none()
            if goods:
                goods.stock -= cart.quantity
                goods.sold_count += cart.quantity

        await self.db.commit()
        await self.db.refresh(order)

        return {
            "order_id": order.id,
            "order_no": order.order_no,
            "pay_amount": float(order.pay_amount),
            "status": order.status,
            "created_at": order.created_at
        }

    async def pay_order(self, order_id: str, user_id: str, pay_method: str = "balance") -> Dict[str, Any]:
        """支付订单"""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.status == OrderStatus.PENDING.value
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("订单不存在或已支付")

        if pay_method == "balance":
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise NotFoundException("用户不存在")

            if user.point < int(order.pay_amount):
                raise BusinessException(f"积分不足，需要 {int(order.pay_amount)} 积分")

            user.point -= int(order.pay_amount)
            user.total_spent += order.pay_amount

        order.status = OrderStatus.PAID.value
        order.pay_method = pay_method
        order.pay_time = datetime.now()
        order.pay_transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

        log = OrderLog(
            order_id=order.id,
            operator=user_id,
            action="pay",
            content=f"支付成功，方式: {pay_method}",
            before_status=OrderStatus.PENDING.value,
            after_status=OrderStatus.PAID.value
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "pay_time": order.pay_time,
            "pay_transaction_id": order.pay_transaction_id
        }

    async def ship_order(self, order_id: str, admin_id: str, logistics_company: str, logistics_no: str) -> Dict[str, Any]:
        """发货"""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.status == OrderStatus.PAID.value
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("订单不存在或状态不正确")

        order.status = OrderStatus.SHIPPED.value
        order.logistics_company = logistics_company
        order.logistics_no = logistics_no
        order.ship_time = datetime.now()

        log = OrderLog(
            order_id=order.id,
            operator=admin_id,
            action="ship",
            content=f"发货，物流: {logistics_company}，单号: {logistics_no}",
            before_status=OrderStatus.PAID.value,
            after_status=OrderStatus.SHIPPED.value
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "logistics_company": order.logistics_company,
            "logistics_no": order.logistics_no,
            "ship_time": order.ship_time
        }

    async def confirm_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """确认收货"""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.status == OrderStatus.SHIPPED.value
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("订单不存在或状态不正确")

        order.status = OrderStatus.COMPLETED.value
        order.confirm_time = datetime.now()

        log = OrderLog(
            order_id=order.id,
            operator=user_id,
            action="confirm",
            content="确认收货",
            before_status=OrderStatus.SHIPPED.value,
            after_status=OrderStatus.COMPLETED.value
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "confirm_time": order.confirm_time
        }

    async def cancel_order(self, order_id: str, user_id: str, reason: str = "") -> Dict[str, Any]:
        """取消订单"""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.status == OrderStatus.PENDING.value
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("订单不存在或状态不正确")

        order.status = OrderStatus.CANCELLED.value
        order.cancel_time = datetime.now()
        order.cancel_reason = reason

        # 恢复库存
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = result.scalars().all()
        for item in items:
            result = await self.db.execute(
                select(Goods).where(Goods.id == item.goods_id)
            )
            goods = result.scalar_one_or_none()
            if goods:
                goods.stock += item.quantity
                goods.sold_count -= item.quantity

        log = OrderLog(
            order_id=order.id,
            operator=user_id,
            action="cancel",
            content=f"取消订单，原因: {reason}",
            before_status=OrderStatus.PENDING.value,
            after_status=OrderStatus.CANCELLED.value
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "cancel_time": order.cancel_time
        }

    async def get_order_detail(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """获取订单详情"""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("订单不存在")

        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = result.scalars().all()

        return {
            "id": order.id,
            "order_no": order.order_no,
            "total_amount": float(order.total_amount),
            "discount_amount": float(order.discount_amount),
            "freight_amount": float(order.freight_amount),
            "pay_amount": float(order.pay_amount),
            "status": order.status,
            "status_name": OrderStatus(order.status).name,
            "pay_method": order.pay_method,
            "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M:%S") if order.pay_time else None,
            "logistics_company": order.logistics_company,
            "logistics_no": order.logistics_no,
            "ship_time": order.ship_time.strftime("%Y-%m-%d %H:%M:%S") if order.ship_time else None,
            "confirm_time": order.confirm_time.strftime("%Y-%m-%d %H:%M:%S") if order.confirm_time else None,
            "receiver_name": order.receiver_name,
            "receiver_phone": order.receiver_phone,
            "receiver_address": order.receiver_address,
            "user_remark": order.user_remark,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
            "items": [{
                "id": i.id,
                "goods_name": i.goods_name,
                "goods_image": i.goods_image,
                "spec_name": i.spec_name,
                "price": float(i.price),
                "quantity": i.quantity,
                "total_amount": float(i.total_amount),
                "is_commented": i.is_commented
            } for i in items]
        }

    async def get_user_orders(
        self,
        user_id: str,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户订单列表"""
        query = select(Order).where(Order.user_id == user_id)

        if status is not None:
            query = query.where(Order.status == status)

        total_result = await self.db.execute(
            select(Order).where(Order.user_id == user_id)
        )
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(desc(Order.created_at)).offset(offset).limit(page_size)
        )
        orders = result.scalars().all()

        return {
            "list": [{
                "id": o.id,
                "order_no": o.order_no,
                "pay_amount": float(o.pay_amount),
                "status": o.status,
                "status_name": OrderStatus(o.status).name,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else None
            } for o in orders],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }