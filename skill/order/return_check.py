from skill.base import SkillParams,BaseSkill
from database.db import SessionLocal
from db.models import Order
class CheckReturnEligibilityParams(SkillParams):
    order_no: str

class CheckReturnEligibilitySkill(BaseSkill):
    name = "check_return_eligibility"
    description = "用户申请退货时调用，校验是否满足退货资格"
    params_model = CheckReturnEligibilityParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == args.order_no).first()
            db.close()
            if not order:
                return "未查询到该订单，无法申请退货"
            if order.status == "refund":
                return "该订单已完成退款，请勿重复申请"
            if order.status == "pending":
                return "订单尚未支付，无需申请退货"
            return "符合退货条件，可以提交退货申请"
        except Exception as e:
            return f"工具异常：{str(e)}"