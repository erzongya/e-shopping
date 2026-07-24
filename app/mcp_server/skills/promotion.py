from typing import Dict, Any, Optional
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.promotion import AsyncPromotionService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class GetCurrentPromotionsParams(SkillParams):
    """获取当前促销参数"""
    pass


class CalculateDiscountParams(SkillParams):
    """计算优惠参数"""
    amount: float = Field(description="订单金额")
    promotion_id: str = Field(description="促销活动ID")


class GetCouponsParams(SkillParams):
    """获取优惠券列表参数"""
    status: int = Field(1, description="状态: 1有效 2已停用")


class ReceiveCouponParams(SkillParams):
    """领取优惠券参数"""
    user_id: str = Field(description="用户ID")
    coupon_id: str = Field(description="优惠券ID")


class GetUserCouponsParams(SkillParams):
    """获取用户优惠券参数"""
    user_id: str = Field(description="用户ID")
    status: Optional[int] = Field(None, description="状态: 1未使用 2已使用 3已过期")


# ========== 技能实现 ==========

class GetCurrentPromotionsSkill(BaseSkill):
    """获取当前促销"""
    name = "get_current_promotions"
    description = "获取当前有效的促销活动"
    params_model = GetCurrentPromotionsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "promotion", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncPromotionService(db)
                result = await service.get_current_promotions()
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "promotion", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class CalculateDiscountSkill(BaseSkill):
    """计算优惠"""
    name = "calculate_discount"
    description = "计算促销优惠金额"
    params_model = CalculateDiscountParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.promotion_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncPromotionService(db)
                result = await service.calculate_discount(
                    amount=args.amount,
                    promotion_id=args.promotion_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.promotion_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetCouponsSkill(BaseSkill):
    """获取优惠券列表"""
    name = "get_coupons"
    description = "获取可领取的优惠券列表"
    params_model = GetCouponsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "coupon", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncPromotionService(db)
                result = await service.get_coupons(status=args.status)
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "coupon", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ReceiveCouponSkill(BaseSkill):
    """领取优惠券"""
    name = "receive_coupon"
    description = "用户领取优惠券"
    params_model = ReceiveCouponParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncPromotionService(db)
                result = await service.receive_coupon(
                    user_id=args.user_id,
                    coupon_id=args.coupon_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetUserCouponsSkill(BaseSkill):
    """获取用户优惠券"""
    name = "get_user_coupons"
    description = "获取用户已领取的优惠券"
    params_model = GetUserCouponsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncPromotionService(db)
                result = await service.get_user_coupons(
                    user_id=args.user_id,
                    status=args.status
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

PROMOTION_SKILL_CLS = [
    GetCurrentPromotionsSkill,
    CalculateDiscountSkill,
    GetCouponsSkill,
    ReceiveCouponSkill,
    GetUserCouponsSkill
]