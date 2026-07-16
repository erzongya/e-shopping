from skill.base import SkillParams, BaseSkill
from database.db import SessionLocal
from db.models import Order
from pydantic import Field

class CheckReturnEligibilityParams(SkillParams):
    """退货资格校验参数，order_no平铺在args顶层，禁止使用kwargs嵌套包裹"""
    order_no: str = Field(
        description="待校验的订单编号，唯一顶层入参，禁止放入kwargs字段"
    )

class CheckReturnEligibilitySkill(BaseSkill):
    name = "check_return_eligibility"
    description = "用户申请退货时调用，校验是否满足退货资格；order_no直接平铺在args顶层，禁止用kwargs打包嵌套参数"
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
            # 异常文案不含kwargs关键词，避免存入记忆误导大模型循环输出错误格式
            return f"退货资格校验失败，错误详情：{str(e)}"