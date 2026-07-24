from typing import Dict, Any, List, Optional
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.order import AsyncOrderService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class CreateOrderParams(SkillParams):
    """创建订单参数"""
    user_id: str = Field(description="用户ID")
    address_id: str = Field(description="收货地址ID")
    cart_ids: List[str] = Field(description="购物车ID列表")
    remark: str = Field("", description="用户备注")


class PayOrderParams(SkillParams):
    """支付订单参数"""
    order_id: str = Field(description="订单ID")
    user_id: str = Field(description="用户ID")
    pay_method: str = Field("balance", description="支付方式: balance/wechat/alipay")


class CancelOrderParams(SkillParams):
    """取消订单参数"""
    order_id: str = Field(description="订单ID")
    user_id: str = Field(description="用户ID")
    reason: str = Field("", description="取消原因")


class GetOrderDetailParams(SkillParams):
    """获取订单详情参数"""
    order_id: str = Field(description="订单ID")
    user_id: str = Field(description="用户ID")


class GetUserOrdersParams(SkillParams):
    """获取用户订单列表参数"""
    user_id: str = Field(description="用户ID")
    status: Optional[int] = Field(None, description="订单状态筛选")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


class ConfirmOrderParams(SkillParams):
    """确认收货参数"""
    order_id: str = Field(description="订单ID")
    user_id: str = Field(description="用户ID")


# ========== 技能实现 ==========

class CreateOrderSkill(BaseSkill):
    """创建订单"""
    name = "create_order"
    description = "根据购物车创建订单"
    params_model = CreateOrderParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.create_order(  # ✅ await
                    user_id=args.user_id,
                    address_id=args.address_id,
                    cart_ids=args.cart_ids,
                    remark=args.remark
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class PayOrderSkill(BaseSkill):
    """支付订单"""
    name = "pay_order"
    description = "支付订单"
    params_model = PayOrderParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.order_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.pay_order(  # ✅ await
                    order_id=args.order_id,
                    user_id=args.user_id,
                    pay_method=args.pay_method
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.order_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class CancelOrderSkill(BaseSkill):
    """取消订单"""
    name = "cancel_order"
    description = "取消订单"
    params_model = CancelOrderParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.order_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.cancel_order(  # ✅ await
                    order_id=args.order_id,
                    user_id=args.user_id,
                    reason=args.reason
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.order_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetOrderDetailSkill(BaseSkill):
    """获取订单详情"""
    name = "get_order_detail"
    description = "获取订单详情"
    params_model = GetOrderDetailParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.order_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.get_order_detail(  # ✅ await
                    order_id=args.order_id,
                    user_id=args.user_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.order_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetUserOrdersSkill(BaseSkill):
    """获取用户订单列表"""
    name = "get_user_orders"
    description = "获取用户订单列表"
    params_model = GetUserOrdersParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.get_user_orders(  # ✅ await
                    user_id=args.user_id,
                    status=args.status,
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ConfirmOrderSkill(BaseSkill):
    """确认收货"""
    name = "confirm_order"
    description = "确认收货，完成订单"
    params_model = ConfirmOrderParams

    async def run(self, **kwargs) -> Dict[str, Any]:  # ✅ async
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.order_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:  # ✅ async with
            try:
                service = AsyncOrderService(db)  # ✅ 异步服务
                result = await service.confirm_order(  # ✅ await
                    order_id=args.order_id,
                    user_id=args.user_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.order_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

ORDER_SKILL_CLS = [
    CreateOrderSkill,
    PayOrderSkill,
    CancelOrderSkill,
    GetOrderDetailSkill,
    GetUserOrdersSkill,
    ConfirmOrderSkill
]