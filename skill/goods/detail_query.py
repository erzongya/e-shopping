from skill.base import SkillParams,BaseSkill
from sqlalchemy.orm import Session
from database.db import SessionLocal
from db.models import Goods
class GetGoodsDetailParams(SkillParams):
    goods_id: str

class GetGoodsDetailSkill(BaseSkill):
    name = "get_goods_detail"
    description = "根据商品ID，查询完整商品详情"
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