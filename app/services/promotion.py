"""
促销业务逻辑服务 - 异步版
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from datetime import datetime

from app.models.promotion import Promotion, Coupon, UserCoupon
from app.models.user import User
from app.common.exceptions import BusinessException, NotFoundException


class AsyncPromotionService:
    """促销业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_promotions(self) -> List[Dict[str, Any]]:
        """获取当前有效的促销活动"""
        now = datetime.now()

        result = await self.db.execute(
            select(Promotion).where(
                Promotion.start_time <= now,
                Promotion.end_time >= now,
                Promotion.status == 2
            )
        )
        promotions = result.scalars().all()

        return [{
            "id": p.id,
            "name": p.name,
            "type": p.type,
            "type_name": self._get_promotion_type_name(p.type),
            "min_amount": float(p.min_amount) if p.min_amount else 0,
            "discount_amount": float(p.discount_amount) if p.discount_amount else 0,
            "discount_rate": float(p.discount_rate) if p.discount_rate else 1.0,
            "start_time": p.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": p.end_time.strftime("%Y-%m-%d %H:%M:%S")
        } for p in promotions]

    async def calculate_discount(self, amount: float, promotion_id: str) -> Dict[str, Any]:
        """计算促销优惠"""
        result = await self.db.execute(
            select(Promotion).where(Promotion.id == promotion_id)
        )
        promotion = result.scalar_one_or_none()
        if not promotion:
            raise NotFoundException("促销活动不存在")

        discount = 0.0

        if promotion.type == 1:  # 满减
            if amount >= float(promotion.min_amount):
                discount = float(promotion.discount_amount)

        elif promotion.type == 2:  # 折扣
            if amount >= float(promotion.min_amount):
                discount = amount * (1 - float(promotion.discount_rate))

        return {
            "promotion_id": promotion.id,
            "promotion_name": promotion.name,
            "original_amount": amount,
            "discount_amount": round(discount, 2),
            "final_amount": round(amount - discount, 2)
        }

    async def get_coupons(self, status: int = 1) -> List[Dict[str, Any]]:
        """获取优惠券列表"""
        now = datetime.now()

        result = await self.db.execute(
            select(Coupon).where(
                Coupon.status == status,
                Coupon.start_time <= now,
                Coupon.end_time >= now,
                Coupon.stock > Coupon.used_count
            )
        )
        coupons = result.scalars().all()

        return [{
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "type": c.type,
            "type_name": "满减券" if c.type == 1 else "折扣券",
            "min_amount": float(c.min_amount) if c.min_amount else 0,
            "discount_amount": float(c.discount_amount) if c.discount_amount else 0,
            "discount_rate": float(c.discount_rate) if c.discount_rate else 1.0,
            "max_discount": float(c.max_discount) if c.max_discount else 0,
            "start_time": c.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": c.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "remaining": c.stock - c.used_count
        } for c in coupons]

    async def receive_coupon(self, user_id: str, coupon_id: str) -> Dict[str, Any]:
        """领取优惠券"""
        # 1. 检查用户
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("用户不存在")

        # 2. 检查优惠券
        result = await self.db.execute(
            select(Coupon).where(
                Coupon.id == coupon_id,
                Coupon.status == 1
            )
        )
        coupon = result.scalar_one_or_none()
        if not coupon:
            raise NotFoundException("优惠券不存在或已停用")

        now = datetime.now()
        if coupon.start_time > now or coupon.end_time < now:
            raise BusinessException("优惠券不在有效期内")

        if coupon.stock <= coupon.used_count:
            raise BusinessException("优惠券已领完")

        # 3. 检查是否已领取
        result = await self.db.execute(
            select(UserCoupon).where(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id,
                UserCoupon.status == 1
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise BusinessException("已领取过该优惠券")

        # 4. 领取优惠券
        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon_id,
            status=1
        )
        self.db.add(user_coupon)

        coupon.used_count += 1

        await self.db.commit()
        await self.db.refresh(user_coupon)

        return {
            "id": user_coupon.id,
            "coupon_id": coupon_id,
            "coupon_name": coupon.name,
            "status": "未使用"
        }

    async def get_user_coupons(self, user_id: str, status: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取用户优惠券"""
        query = select(UserCoupon).where(UserCoupon.user_id == user_id)

        if status is not None:
            query = query.where(UserCoupon.status == status)

        query = query.order_by(desc(UserCoupon.created_at))
        result = await self.db.execute(query)
        user_coupons = result.scalars().all()

        result_list = []
        for uc in user_coupons:
            coupon_result = await self.db.execute(
                select(Coupon).where(Coupon.id == uc.coupon_id)
            )
            coupon = coupon_result.scalar_one_or_none()
            if coupon:
                result_list.append({
                    "id": uc.id,
                    "coupon_id": uc.coupon_id,
                    "coupon_name": coupon.name,
                    "type": coupon.type,
                    "type_name": "满减券" if coupon.type == 1 else "折扣券",
                    "min_amount": float(coupon.min_amount) if coupon.min_amount else 0,
                    "discount_amount": float(coupon.discount_amount) if coupon.discount_amount else 0,
                    "status": uc.status,
                    "status_name": "未使用" if uc.status == 1 else "已使用" if uc.status == 2 else "已过期",
                    "expire_time": coupon.end_time.strftime("%Y-%m-%d %H:%M:%S") if coupon.end_time else None
                })

        return result_list

    def _get_promotion_type_name(self, type: int) -> str:
        """获取促销类型名称"""
        types = {
            1: "满减",
            2: "折扣",
            3: "秒杀",
            4: "优惠券"
        }
        return types.get(type, "未知")