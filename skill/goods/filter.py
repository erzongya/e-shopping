from skill.base import SkillParams,BaseSkill
from typing import List,Optional

class FilterGoodsParams(SkillParams):
    goods_list: List[dict]
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    only_in_stock: bool = True

class FilterGoodsSkill(BaseSkill):
    name = "filter_goods"
    description = "拿到商品列表后，按预算、库存过滤商品"
    params_model = FilterGoodsParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            res = []
            for item in args.goods_list:
                if args.only_in_stock and item["stock"] <= 0:
                    continue
                if args.min_price is not None and item["price"] < args.min_price:
                    continue
                if args.max_price is not None and item["price"] > args.max_price:
                    continue
                res.append(item)
            return res
        except Exception as e:
            return f"工具异常：{str(e)}"