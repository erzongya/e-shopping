from skill.base import SkillParams, BaseSkill
from database.db import SessionLocal
from db.models import Order
from pydantic import Field

class QueryOrderParams(SkillParams):
    """订单查询参数，order_no 平铺在args顶层，禁止使用kwargs嵌套包裹"""
    order_no: str = Field(
        description="订单编号，唯一顶层入参，禁止放入kwargs字段"
    )

class QueryOrderSkill(BaseSkill):
    name = "query_order"
    description = "根据订单号order_no查询订单详情；参数直接平铺在args顶层，禁止用kwargs打包嵌套参数"
    params_model = QueryOrderParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == args.order_no).first()
            db.close()
            if not order:
                return {"msg": "未查询到对应订单数据"}
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
            # 异常文案不出现kwargs关键词，避免存入记忆误导LLM
            return f"查询订单信息失败，错误详情：{str(e)}"