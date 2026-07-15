from skill.base import SkillParams,BaseSkill
from database.db import SessionLocal
from db.models import Order
class QueryOrderParams(SkillParams):
    order_no: str

class QueryOrderSkill(BaseSkill):
    name = "query_order"
    description = "用户查询订单、咨询订单金额/状态时调用"
    params_model = QueryOrderParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == args.order_no).first()
            db.close()
            if not order:
                return {}
            order_data = {
                "order_id": order.id,
                "user_id": order.user_id,
                "goods_id": order.goods_id,
                "origin_price": float(order.origin_price),
                "real_pay": float(order.real_pay),
                "status": order.status
            }
            return order_data
        except Exception as e:
            return f"工具异常：{str(e)}"