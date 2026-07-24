from typing import Dict, Any, Optional
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.cart import AsyncCartService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class AddToCartParams(SkillParams):
    """添加到购物车参数"""
    user_id: str = Field(description="用户ID")
    goods_id: str = Field(description="商品ID")
    quantity: int = Field(1, description="数量")
    spec_id: Optional[str] = Field(None, description="规格ID")


class UpdateCartParams(SkillParams):
    """更新购物车参数"""
    cart_id: str = Field(description="购物车ID")
    user_id: str = Field(description="用户ID")
    quantity: int = Field(description="新数量")


class RemoveFromCartParams(SkillParams):
    """移除购物车参数"""
    cart_id: str = Field(description="购物车ID")
    user_id: str = Field(description="用户ID")


class ToggleSelectParams(SkillParams):
    """切换选中状态参数"""
    cart_id: str = Field(description="购物车ID")
    user_id: str = Field(description="用户ID")


class ClearCartParams(SkillParams):
    """清空购物车参数"""
    user_id: str = Field(description="用户ID")


class GetCartListParams(SkillParams):
    """获取购物车列表参数"""
    user_id: str = Field(description="用户ID")


# ========== 技能实现 ==========

class AddToCartSkill(BaseSkill):
    """添加到购物车"""
    name = "add_to_cart"
    description = "添加商品到购物车"
    params_model = AddToCartParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.add_to_cart(
                    user_id=args.user_id,
                    goods_id=args.goods_id,
                    quantity=args.quantity,
                    spec_id=args.spec_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class UpdateCartSkill(BaseSkill):
    """更新购物车"""
    name = "update_cart"
    description = "更新购物车商品数量"
    params_model = UpdateCartParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.cart_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.update_quantity(
                    cart_id=args.cart_id,
                    user_id=args.user_id,
                    quantity=args.quantity
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.cart_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class RemoveFromCartSkill(BaseSkill):
    """移除购物车"""
    name = "remove_from_cart"
    description = "从购物车移除商品"
    params_model = RemoveFromCartParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.cart_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.remove_from_cart(
                    cart_id=args.cart_id,
                    user_id=args.user_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.cart_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ToggleSelectSkill(BaseSkill):
    """切换选中状态"""
    name = "toggle_select"
    description = "切换购物车商品的选中状态"
    params_model = ToggleSelectParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.cart_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.toggle_select(
                    cart_id=args.cart_id,
                    user_id=args.user_id
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.cart_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ClearCartSkill(BaseSkill):
    """清空购物车"""
    name = "clear_cart"
    description = "清空用户购物车"
    params_model = ClearCartParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.clear_cart(user_id=args.user_id)
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetCartListSkill(BaseSkill):
    """获取购物车列表"""
    name = "get_cart_list"
    description = "获取用户购物车列表"
    params_model = GetCartListParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncCartService(db)
                result = await service.get_cart_list(user_id=args.user_id)
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

CART_SKILL_CLS = [
    AddToCartSkill,
    UpdateCartSkill,
    RemoveFromCartSkill,
    ToggleSelectSkill,
    ClearCartSkill,
    GetCartListSkill
]