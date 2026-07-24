"""
售后 MCP 技能 - 异步版
"""
from typing import Dict, Any, Optional
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.aftersale import AsyncAfterSaleService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class ApplyRefundParams(SkillParams):
    """申请售后参数"""
    user_id: str = Field(description="用户ID")
    order_id: str = Field(description="订单ID")
    order_item_id: str = Field(description="订单明细ID")
    type: int = Field(description="售后类型: 1仅退款 2退货退款")
    reason: str = Field(description="申请原因")
    description: str = Field("", description="详细描述")
    images: str = Field("", description="凭证图片JSON")


class GetAftersaleDetailParams(SkillParams):
    """获取售后详情参数"""
    aftersale_id: str = Field(description="售后ID")
    user_id: str = Field(description="用户ID")


class GetUserAftersalesParams(SkillParams):
    """获取用户售后列表参数"""
    user_id: str = Field(description="用户ID")
    status: Optional[int] = Field(None, description="状态筛选")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


# ========== 技能实现 ==========

class ApplyRefundSkill(BaseSkill):
    """申请售后"""
    name = "apply_refund"
    description = "申请退款或退货退款"
    params_model = ApplyRefundParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.order_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAfterSaleService(db)
                result = await service.apply_refund(
                    user_id=args.user_id,
                    order_id=args.order_id,
                    order_item_id=args.order_item_id,
                    type=args.type,
                    reason=args.reason,
                    description=args.description,
                    images=args.images
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.order_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetAftersaleDetailSkill(BaseSkill):
    """获取售后详情"""
    name = "get_aftersale_detail"
    description = "获取售后申请详情"
    params_model = GetAftersaleDetailParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.aftersale_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAfterSaleService(db)
                result = await service.get_aftersale_detail(
                    aftersale_id=args.aftersale_id,
                    user_id=args.user_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.aftersale_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetUserAftersalesSkill(BaseSkill):
    """获取用户售后列表"""
    name = "get_user_aftersales"
    description = "获取用户售后申请列表"
    params_model = GetUserAftersalesParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAfterSaleService(db)
                result = await service.get_user_aftersales(
                    user_id=args.user_id,
                    status=args.status,
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

AFTERSALE_SKILL_CLS = [
    ApplyRefundSkill,
    GetAftersaleDetailSkill,
    GetUserAftersalesSkill
]