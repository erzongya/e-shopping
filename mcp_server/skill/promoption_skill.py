from mcp_server.skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.promoption_models import ActivityCoupon, UserCoupon, ActivityFlash
import uuid
from datetime import datetime
from common.logger import log_info, log_error

class QueryUserCouponParams(SkillParams):
    user_id: str

class ReceiveCouponParams(SkillParams):
    user_id: str
    activity_coupon_id: str

class QueryFlashGoodsParams(SkillParams):
    pass

# 查询用户所有优惠券
class QueryUserCouponSkill(BaseSkill):
    name = "query_user_coupon"
    description = "查询用户已领取的全部优惠券，区分已使用/未使用"
    params_model = QueryUserCouponParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            rows = db.query(UserCoupon, ActivityCoupon)\
                .join(ActivityCoupon, UserCoupon.activity_id == ActivityCoupon.id)\
                .filter(UserCoupon.user_id == args.user_id).all()
            arr = []
            for uc, act in rows:
                arr.append({
                    "user_coupon_id": uc.id,
                    "coupon_name": act.coupon_name,
                    "full_limit": float(act.full_limit),
                    "discount": float(act.discount),
                    "expire_time": act.expire_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_used": uc.is_used
                })
            log_info(trace_id, session_id, f"用户{user_id}优惠券查询完成，共{len(arr)}张")
            return {"code":0, "coupon_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询优惠券异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 领取优惠券
class ReceiveCouponSkill(BaseSkill):
    name = "receive_coupon"
    description = "用户领取活动优惠券，校验库存上限"
    params_model = ReceiveCouponParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        coupon_act_id = args.activity_coupon_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}, coupon_act_id={coupon_act_id}")
        try:
            act = db.query(ActivityCoupon).filter(ActivityCoupon.id == coupon_act_id).first()
            if not act:
                log_info(trace_id, session_id, f"优惠券活动{coupon_act_id}不存在")
                return {"code":-1, "msg":"优惠券活动不存在"}
            if act.receive_count >= act.total_limit:
                log_info(trace_id, session_id, f"优惠券{coupon_act_id}已领完")
                return {"code":-1, "msg":"优惠券已领完"}
            exist = db.query(UserCoupon).filter(
                UserCoupon.user_id == args.user_id,
                UserCoupon.activity_id == coupon_act_id
            ).first()
            if exist:
                log_info(trace_id, session_id, f"用户已领取该券，不可重复领取")
                return {"code":-1, "msg":"已领取过该券，不可重复领取"}
            new_uc = UserCoupon(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                activity_id=coupon_act_id,
                is_used=0,
                create_time=datetime.now()
            )
            act.receive_count += 1
            db.add(new_uc)
            db.commit()
            log_info(trace_id, session_id, f"用户{user_id}领取优惠券{coupon_act_id}成功")
            return {"code":0, "msg":"领取优惠券成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}领券异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 查询全部秒杀活动商品
class QueryFlashGoodsSkill(BaseSkill):
    name = "query_flash_goods"
    description = "查询当前所有秒杀活动及对应商品ID、库存、活动时间"
    params_model = QueryFlashGoodsParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        session_id = "flash_query"
        log_info(trace_id, session_id, f"执行工具{self.name}查询全部秒杀活动")
        try:
            flash_list = db.query(ActivityFlash).all()
            arr = []
            for f in flash_list:
                arr.append({
                    "flash_id": f.id,
                    "goods_id": f.goods_id,
                    "flash_start": f.flash_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "flash_end": f.flash_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "stock_total": f.stock_total
                })
            log_info(trace_id, session_id, f"秒杀活动查询完成，共{len(arr)}场活动")
            return {"code":0, "flash_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询秒杀活动异常", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

PROMOPTION_SKILL_CLS = [
    QueryUserCouponSkill,
    ReceiveCouponSkill,
    QueryFlashGoodsSkill
]