"""
商品 MCP 技能 - 异步版
"""
from typing import Dict, Any, Optional
from pydantic import Field, field_validator

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.goods import GoodsService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class QueryGoodsDetailParams(SkillParams):
    """查询商品详情参数"""
    goods_id: str = Field(description="商品唯一ID")


class ListGoodsByFilterParams(SkillParams):
    """商品列表筛选参数"""
    category: Optional[str] = Field(None, description="商品分类")
    sub_category: Optional[str] = Field(None, description="子分类")
    brand: Optional[str] = Field(None, description="品牌")
    min_price: Optional[float] = Field(None, description="最低价格")
    max_price: Optional[float] = Field(None, description="最高价格")
    is_flash: Optional[int] = Field(None, description="是否秒杀: 1是 0否")
    is_hot: Optional[bool] = Field(None, description="是否热卖")
    is_new: Optional[bool] = Field(None, description="是否新品")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


class GetFlashGoodsParams(SkillParams):
    """获取秒杀商品参数"""
    pass


class QueryGoodsSpecParams(SkillParams):
    """查询商品规格参数"""
    goods_id: str = Field(description="商品ID")


class QueryGoodsCommentParams(SkillParams):
    """查询商品评论参数"""
    goods_id: str = Field(description="商品ID")
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")


class GetGoodsCategoriesParams(SkillParams):
    """获取商品分类参数"""
    parent_id: Optional[str] = Field("0", description="父分类ID")

    @field_validator("parent_id", mode="before")
    @classmethod
    def convert_parent_id(cls, v):
        """将 int 转换为 str"""
        if isinstance(v, int):
            return str(v)
        return v

# ========== 技能实现 ==========

class QueryGoodsDetailSkill(BaseSkill):
    """查询商品详情 - 异步"""
    name = "query_goods_detail"
    description = "根据商品ID查询商品完整基础信息，包含价格、库存、规格等"
    params_model = QueryGoodsDetailParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.goods_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                data = await service.get_detail(args.goods_id)
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, args.goods_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ListGoodsByFilterSkill(BaseSkill):
    """商品列表筛选 - 异步"""
    name = "list_goods_by_filter"
    description = "按分类、价格、品牌、秒杀等多条件查询商品列表"
    params_model = ListGoodsByFilterParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "goods_filter", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                result = await service.list_by_filter(
                    category=args.category,
                    sub_category=args.sub_category,
                    brand=args.brand,
                    min_price=args.min_price,
                    max_price=args.max_price,
                    is_flash=args.is_flash,
                    is_hot=args.is_hot,
                    is_new=args.is_new,
                    keyword=args.keyword,
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "goods_filter", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetFlashGoodsSkill(BaseSkill):
    """获取秒杀商品 - 异步"""
    name = "get_flash_goods"
    description = "获取当前正在进行的秒杀商品列表"
    params_model = GetFlashGoodsParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "flash_goods", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                data = await service.get_flash_goods()
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, "flash_goods", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class QueryGoodsSpecSkill(BaseSkill):
    """查询商品规格 - 异步"""
    name = "query_goods_spec"
    description = "查询商品全部规格，含规格加价、独立库存"
    params_model = QueryGoodsSpecParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.goods_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                data = await service.get_specs(args.goods_id)
                return {"code": 0, "spec_list": data}
            except Exception as e:
                log_error(trace_id, args.goods_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class QueryGoodsCommentSkill(BaseSkill):
    """查询商品评论 - 异步"""
    name = "query_goods_comment"
    description = "查询商品全部用户评价，含评分、标签、内容"
    params_model = QueryGoodsCommentParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.goods_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                result = await service.get_comments(
                    goods_id=args.goods_id,
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, args.goods_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetGoodsCategoriesSkill(BaseSkill):
    """获取商品分类 - 异步"""
    name = "get_goods_categories"
    description = "获取商品分类列表"
    params_model = GetGoodsCategoriesParams

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "categories", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = GoodsService(db)
                data = await service.get_categories(parent_id=args.parent_id)
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, "categories", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

GOODS_SKILL_CLS = [
    QueryGoodsDetailSkill,
    ListGoodsByFilterSkill,
    GetFlashGoodsSkill,
    QueryGoodsSpecSkill,
    QueryGoodsCommentSkill,
    GetGoodsCategoriesSkill,
]