from mcp_server.skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.user_models import UserInfo, UserAddress, UserSignIn
import uuid
from datetime import datetime
from common.logger import log_info, log_error

# ========== 参数 ==========
class QueryUserInfoParams(SkillParams):
    user_id: str

class AddUserAddressParams(SkillParams):
    user_id: str
    name: str
    phone: str
    address: str

class ListUserAddressParams(SkillParams):
    user_id: str

class SignInUserParams(SkillParams):
    user_id: str

# ========== 查询用户基础信息 ==========
class QueryUserInfoSkill(BaseSkill):
    name = "query_user_info"
    description = "查询用户昵称、手机号、会员等级、可用积分"
    params_model = QueryUserInfoParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            u = db.query(UserInfo).filter(UserInfo.id == args.user_id).first()
            if not u:
                log_info(trace_id, session_id, f"用户{user_id}不存在")
                return {"code":-1, "msg":"用户不存在"}
            data = {
                "user_id": u.id,
                "nickname": u.nickname,
                "phone": u.phone,
                "vip_level": u.vip_level,
                "point": u.point
            }
            log_info(trace_id, session_id, f"用户{user_id}信息查询成功")
            return {"code":0, "data":data}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询用户异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# ========== 添加收货地址 ==========
class AddUserAddressSkill(BaseSkill):
    name = "add_user_address"
    description = "新增用户收货地址"
    params_model = AddUserAddressParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            addr = UserAddress(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                name=args.name,
                phone=args.phone,
                address=args.address
            )
            db.add(addr)
            db.commit()
            log_info(trace_id, session_id, f"用户{user_id}新增地址成功")
            return {"code":0, "msg":"地址添加成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}新增地址异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# ========== 查询用户全部地址 ==========
class ListUserAddressSkill(BaseSkill):
    name = "list_user_address"
    description = "查询用户所有收货地址列表"
    params_model = ListUserAddressParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            addrs = db.query(UserAddress).filter(UserAddress.user_id == args.user_id).all()
            res = []
            for a in addrs:
                res.append({
                    "addr_id": a.id,
                    "name": a.name,
                    "phone": a.phone,
                    "address": a.address
                })
            log_info(trace_id, session_id, f"用户{user_id}地址查询完成，共{len(res)}条")
            return {"code":0, "address_list": res}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询地址异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# ========== 用户签到领积分 ==========
class SignInUserSkill(BaseSkill):
    name = "user_sign_in"
    description = "用户每日签到，获取积分，同一天不可重复签到"
    params_model = SignInUserParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            exist = db.query(UserSignIn).filter(
                UserSignIn.user_id == args.user_id,
                UserSignIn.sign_date == today
            ).first()
            if exist:
                log_info(trace_id, session_id, f"用户{user_id}今日已签到")
                return {"code":-1, "msg":"今日已签到，请勿重复操作"}
            sign = UserSignIn(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                sign_date=today,
                reward_point=10,
                create_time=datetime.now()
            )
            db.add(sign)
            user = db.query(UserInfo).filter(UserInfo.id == args.user_id).first()
            user.point += 10
            db.commit()
            log_info(trace_id, session_id, f"用户{user_id}签到成功，+10积分")
            return {"code":0, "msg":"签到成功，获得10积分"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}签到异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

USER_SKILL_CLS = [
    QueryUserInfoSkill,
    AddUserAddressSkill,
    ListUserAddressSkill,
    SignInUserSkill
]