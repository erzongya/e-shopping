from skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.aftersale_models import OrderRefund, ComplaintTicket, ManualTicket
import uuid
from datetime import datetime
from common.logger import log_info, log_error

class ApplyRefundParams(SkillParams):
    user_id: str
    order_id: str
    refund_type: str = Field(description="only_refund / return_refund")
    reason: str
    refund_amount: float

class QueryUserRefundParams(SkillParams):
    user_id: str

class CreateComplaintParams(SkillParams):
    user_id: str
    order_id: str
    complaint_type: str
    description: str

# 申请退款
class ApplyRefundSkill(BaseSkill):
    name = "apply_refund"
    description = "提交售后退款工单，仅退款/退货退款两种类型"
    params_model = ApplyRefundParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        order_id = args.order_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}, order_id={order_id}")
        try:
            refund = OrderRefund(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                order_id=args.order_id,
                refund_type=args.refund_type,
                reason=args.reason,
                refund_amount=args.refund_amount,
                status="pending",
                create_time=datetime.now()
            )
            db.add(refund)
            db.commit()
            log_info(trace_id, session_id, f"用户{user_id}订单{order_id}退款申请提交成功")
            return {"code":0, "msg":"退款申请提交成功，等待商家审核"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}提交退款工单异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 查询用户全部退款工单
class QueryUserRefundSkill(BaseSkill):
    name = "query_user_refund"
    description = "查询用户所有退款工单及审核状态"
    params_model = QueryUserRefundParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            refunds = db.query(OrderRefund).filter(OrderRefund.user_id == args.user_id).all()
            arr = []
            for r in refunds:
                arr.append({
                    "refund_id": r.id,
                    "order_id": r.order_id,
                    "refund_type": r.refund_type,
                    "refund_amount": float(r.refund_amount),
                    "status": r.status,
                    "reason": r.reason,
                    "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            log_info(trace_id, session_id, f"用户{user_id}退款工单查询完成，共{len(arr)}条")
            return {"code":0, "refund_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询退款工单异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 创建投诉工单
class CreateComplaintSkill(BaseSkill):
    name = "create_complaint"
    description = "提交商品投诉工单（破损/发货慢/假货等）"
    params_model = CreateComplaintParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        order_id = args.order_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}, order_id={order_id}")
        try:
            cmp = ComplaintTicket(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                order_id=args.order_id,
                complaint_type=args.complaint_type,
                description=args.description,
                status="pending",
                create_time=datetime.now()
            )
            db.add(cmp)
            db.commit()
            log_info(trace_id, session_id, f"用户{user_id}订单{order_id}投诉工单提交成功")
            return {"code":0, "msg":"投诉工单提交成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}提交投诉异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

AFTERSALE_SKILL_CLS = [
    ApplyRefundSkill,
    QueryUserRefundSkill,
    CreateComplaintSkill
]