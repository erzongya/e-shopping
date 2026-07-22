from mcp_server.skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.order_models import UserOrder, OrderLogistics
import uuid
from datetime import datetime
from common.logger import log_info, log_error

# 查询用户订单列表参数
class QueryOrderByUserParams(SkillParams):
    user_id: str | None = Field(None, description="用户ID，选填")
    order_no: str | None = Field(None, description="订单编号，选填，可单独使用单号查询订单")
    status: str | None = Field(None, description="订单状态过滤，选填")

# 查询订单物流轨迹参数
class QueryLogisticsParams(SkillParams):
    tracking_no: str

# 查询用户订单列表工具
class QueryOrderByUserSkill(BaseSkill):
    name = "query_user_order"
    description = "支持【用户ID】或者【订单编号order_no】任意一个条件独立查询订单，两个参数只需要传其中一个即可，不需要同时填写；支持status状态额外过滤"
    params_model = QueryOrderByUserParams

    def run(self, **kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(**kwargs)
        session_id = args.user_id if args.user_id else args.order_no
        log_info(trace_id, session_id,
                 f"执行工具{self.name}，user_id={args.user_id}, order_no={args.order_no}, status={args.status}")
        try:
            q = db.query(UserOrder)
            if args.user_id:
                q = q.filter(UserOrder.user_id == args.user_id)
            if args.order_no:
                q = q.filter(UserOrder.order_no == args.order_no)
            if args.status:
                q = q.filter(UserOrder.status == args.status)
            orders = q.all()
            arr = []
            for o in orders:
                arr.append({
                    "order_id": o.id,
                    "order_no": o.order_no,
                    "goods_id": o.goods_id,
                    "buy_num": o.buy_num,
                    "pay_price": float(o.pay_price),
                    "status": o.status,
                    "tracking_no": o.tracking_no,
                    "create_time": o.create_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            log_info(trace_id, session_id, f"订单查询完成，共{len(arr)}条")
            return {"code": 0, "order_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询订单异常", e)
            return {"code": -1, "msg": str(e)}
        finally:
            db.close()

# 查询物流轨迹
class QueryLogisticsSkill(BaseSkill):
    name = "query_logistics_track"
    description = "根据快递单号查询完整物流节点轨迹"
    params_model = QueryLogisticsParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        track_no = args.tracking_no
        session_id = "logistics_op"
        log_info(trace_id, session_id, f"执行工具{self.name}，tracking_no={track_no}")
        try:
            logs = db.query(OrderLogistics).filter(OrderLogistics.tracking_no == track_no).all()
            arr = []
            for log in logs:
                arr.append({
                    "track_time": log.track_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "track_info": log.track_info
                })
            log_info(trace_id, session_id, f"单号{track_no}物流轨迹查询完成，共{len(arr)}条节点")
            return {"code":0, "logistics_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询物流异常，tracking_no={track_no}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

ORDER_SKILL_CLS = [
    QueryOrderByUserSkill,
    QueryLogisticsSkill
]