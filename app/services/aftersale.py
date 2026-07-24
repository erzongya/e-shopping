"""
售后业务逻辑服务 - 异步版
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime

from app.models.aftersale import AfterSale
from app.models.order import Order, OrderItem
from app.models.goods import Goods
from app.common.exceptions import BusinessException, NotFoundException
from app.common.enums import OrderStatus, AfterSaleStatus


class AsyncAfterSaleService:
    """售后业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_refund(
        self,
        user_id: str,
        order_id: str,
        order_item_id: str,
        type: int,
        reason: str,
        description: str = "",
        images: str = "",
        refund_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """申请售后"""
        # 1. 检查订单
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id
            )
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException("订单不存在")

        # 2. 检查订单状态
        if order.status not in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value, OrderStatus.COMPLETED.value]:
            raise BusinessException("当前订单状态不支持售后")

        # 3. 检查订单明细
        result = await self.db.execute(
            select(OrderItem).where(
                OrderItem.id == order_item_id,
                OrderItem.order_id == order_id
            )
        )
        order_item = result.scalar_one_or_none()
        if not order_item:
            raise NotFoundException("订单商品不存在")

        # 4. 检查是否已申请售后
        result = await self.db.execute(
            select(AfterSale).where(
                AfterSale.order_item_id == order_item_id,
                AfterSale.status.in_([1, 2, 4])
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise BusinessException("该商品已申请售后，请勿重复提交")

        # 5. 计算退款金额
        if refund_amount is None:
            refund_amount = float(order_item.total_amount)
        else:
            if refund_amount > float(order_item.total_amount):
                raise BusinessException("退款金额不能超过商品金额")

        # 6. 创建售后申请
        aftersale = AfterSale(
            order_id=order_id,
            order_item_id=order_item_id,
            user_id=user_id,
            type=type,
            reason=reason,
            description=description,
            images=images,
            refund_amount=refund_amount,
            status=AfterSaleStatus.PENDING.value
        )

        self.db.add(aftersale)

        # 7. 更新订单状态为退款中
        if order.status != OrderStatus.REFUNDING.value:
            order.status = OrderStatus.REFUNDING.value

        await self.db.commit()
        await self.db.refresh(aftersale)

        return {
            "id": aftersale.id,
            "order_id": order_id,
            "type": type,
            "type_name": "仅退款" if type == 1 else "退货退款",
            "status": aftersale.status,
            "status_name": "待审核",
            "refund_amount": float(aftersale.refund_amount),
            "created_at": aftersale.created_at
        }

    async def audit_aftersale(
        self,
        aftersale_id: str,
        admin_id: str,
        approved: bool,
        remark: str = ""
    ) -> Dict[str, Any]:
        """审核售后申请"""
        result = await self.db.execute(
            select(AfterSale).where(
                AfterSale.id == aftersale_id,
                AfterSale.status == AfterSaleStatus.PENDING.value
            )
        )
        aftersale = result.scalar_one_or_none()
        if not aftersale:
            raise NotFoundException("售后申请不存在或已处理")

        if approved:
            aftersale.status = AfterSaleStatus.APPROVED.value

            if aftersale.type == 1:
                aftersale.status = AfterSaleStatus.COMPLETED.value
                aftersale.complete_time = datetime.now()
                aftersale.refund_time = datetime.now()
                aftersale.refund_transaction_id = f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"

                result = await self.db.execute(
                    select(OrderItem).where(OrderItem.id == aftersale.order_item_id)
                )
                order_item = result.scalar_one_or_none()
                if order_item:
                    result = await self.db.execute(
                        select(Goods).where(Goods.id == order_item.goods_id)
                    )
                    goods = result.scalar_one_or_none()
                    if goods:
                        goods.stock += order_item.quantity
                        goods.sold_count -= order_item.quantity
        else:
            aftersale.status = AfterSaleStatus.REJECTED.value
            aftersale.reject_time = datetime.now()
            aftersale.reject_reason = remark

        aftersale.audit_time = datetime.now()
        aftersale.audit_remark = remark

        await self.db.commit()
        await self.db.refresh(aftersale)

        return {
            "id": aftersale.id,
            "status": aftersale.status,
            "status_name": "审核通过" if approved else "审核拒绝",
            "remark": remark
        }

    async def return_goods(
        self,
        aftersale_id: str,
        user_id: str,
        logistics_company: str,
        logistics_no: str
    ) -> Dict[str, Any]:
        """退货"""
        result = await self.db.execute(
            select(AfterSale).where(
                AfterSale.id == aftersale_id,
                AfterSale.user_id == user_id,
                AfterSale.status == AfterSaleStatus.APPROVED.value,
                AfterSale.type == 2
            )
        )
        aftersale = result.scalar_one_or_none()
        if not aftersale:
            raise NotFoundException("售后申请不存在或状态不正确")

        aftersale.status = AfterSaleStatus.RETURNING.value
        aftersale.return_logistics_company = logistics_company
        aftersale.return_logistics_no = logistics_no

        await self.db.commit()
        await self.db.refresh(aftersale)

        return {
            "id": aftersale.id,
            "status": aftersale.status,
            "status_name": "退货中",
            "logistics_company": logistics_company,
            "logistics_no": logistics_no
        }

    async def confirm_return_received(
        self,
        aftersale_id: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """确认收货（管理员确认收到退货）"""
        result = await self.db.execute(
            select(AfterSale).where(
                AfterSale.id == aftersale_id,
                AfterSale.status == AfterSaleStatus.RETURNING.value,
                AfterSale.type == 2
            )
        )
        aftersale = result.scalar_one_or_none()
        if not aftersale:
            raise NotFoundException("售后申请不存在或状态不正确")

        aftersale.status = AfterSaleStatus.COMPLETED.value
        aftersale.return_receive_time = datetime.now()
        aftersale.complete_time = datetime.now()
        aftersale.refund_time = datetime.now()
        aftersale.refund_transaction_id = f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == aftersale.order_item_id)
        )
        order_item = result.scalar_one_or_none()
        if order_item:
            result = await self.db.execute(
                select(Goods).where(Goods.id == order_item.goods_id)
            )
            goods = result.scalar_one_or_none()
            if goods:
                goods.stock += order_item.quantity
                goods.sold_count -= order_item.quantity

        await self.db.commit()
        await self.db.refresh(aftersale)

        return {
            "id": aftersale.id,
            "status": aftersale.status,
            "status_name": "已完成",
            "refund_time": aftersale.refund_time
        }

    async def get_aftersale_detail(self, aftersale_id: str, user_id: str) -> Dict[str, Any]:
        """获取售后详情"""
        result = await self.db.execute(
            select(AfterSale).where(
                AfterSale.id == aftersale_id,
                AfterSale.user_id == user_id
            )
        )
        aftersale = result.scalar_one_or_none()
        if not aftersale:
            raise NotFoundException("售后申请不存在")

        return {
            "id": aftersale.id,
            "order_id": aftersale.order_id,
            "order_item_id": aftersale.order_item_id,
            "type": aftersale.type,
            "type_name": "仅退款" if aftersale.type == 1 else "退货退款",
            "reason": aftersale.reason,
            "description": aftersale.description,
            "images": aftersale.images,
            "refund_amount": float(aftersale.refund_amount),
            "status": aftersale.status,
            "status_name": self._get_status_name(aftersale.status),
            "audit_remark": aftersale.audit_remark,
            "reject_reason": aftersale.reject_reason,
            "return_logistics_company": aftersale.return_logistics_company,
            "return_logistics_no": aftersale.return_logistics_no,
            "created_at": aftersale.created_at.strftime("%Y-%m-%d %H:%M:%S") if aftersale.created_at else None
        }

    async def get_user_aftersales(
        self,
        user_id: str,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取用户售后列表"""
        query = select(AfterSale).where(AfterSale.user_id == user_id)

        if status is not None:
            query = query.where(AfterSale.status == status)

        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(desc(AfterSale.created_at)).offset(offset).limit(page_size)
        )
        aftersales = result.scalars().all()

        return {
            "list": [{
                "id": a.id,
                "order_id": a.order_id,
                "type": a.type,
                "type_name": "仅退款" if a.type == 1 else "退货退款",
                "refund_amount": float(a.refund_amount),
                "status": a.status,
                "status_name": self._get_status_name(a.status),
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None
            } for a in aftersales],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    def _get_status_name(self, status: int) -> str:
        """获取状态名称"""
        names = {
            1: "待审核",
            2: "审核通过",
            3: "审核拒绝",
            4: "退货中",
            5: "已完成",
            6: "已关闭"
        }
        return names.get(status, "未知")