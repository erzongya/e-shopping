from skill.base import SkillParams,BaseSkill
from sqlalchemy.orm import Session
from database.db import SessionLocal
from db.models import Goods
from pydantic import Field
class GetGoodsDetailParams(SkillParams):
    """商品详情查询参数，仅支持顶层goods_id，禁止使用kwargs嵌套包裹"""
    goods_id: str = Field(
        description="商品唯一ID，必填顶层参数，不要放入kwargs字段"
    )

class GetGoodsDetailSkill(BaseSkill):
    name = "get_goods_detail"
    description = "根据商品ID(goods_id)查询商品完整详情；所有参数直接平铺在args顶层，禁止用kwargs打包参数"
    params_model = GetGoodsDetailParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            db: Session = SessionLocal()
            goods = db.query(Goods).filter(Goods.id == args.goods_id).all()
            db.close()
            data = [
                {
                    "id": g.id,
                    "name": g.name,
                    "category": g.category,
                    "price": g.price,
                    "stock": g.stock,
                    "desc": g.desc
                }
                for g in goods
            ]
            return data
        except Exception as e:
            return f"工具异常：{str(e)}"