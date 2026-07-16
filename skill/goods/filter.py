from skill.base import SkillParams, BaseSkill
from typing import List, Optional
from pydantic import Field

class FilterGoodsParams(SkillParams):
    """商品过滤参数，全部参数平铺在args顶层，禁止使用kwargs嵌套包裹"""
    goods_list: List[dict] = Field(description="待过滤的原始商品列表，必填顶层参数")
    min_price: Optional[float] = Field(None, description="最低价格筛选，不传则不限制最低价")
    max_price: Optional[float] = Field(None, description="最高价格筛选，不传则不限制最高价")
    only_in_stock: bool = Field(True, description="是否仅保留有库存商品，默认true")

class FilterGoodsSkill(BaseSkill):
    name = "filter_goods"
    description = "传入商品列表，按价格区间、库存状态过滤商品；所有参数直接平铺在args顶层，禁止用kwargs打包嵌套参数"
    params_model = FilterGoodsParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            res = []
            for item in args.goods_list:
                # 过滤无库存商品
                if args.only_in_stock and item.get("stock", 0) <= 0:
                    continue
                # 最低价格过滤
                if args.min_price is not None and item.get("price", 0) < args.min_price:
                    continue
                # 最高价格过滤
                if args.max_price is not None and item.get("price", 0) > args.max_price:
                    continue
                res.append(item)
            return res
        except Exception as e:
            # 异常文案不含kwargs关键词，避免污染对话记忆误导LLM
            return f"商品过滤处理失败，错误信息：{str(e)}"