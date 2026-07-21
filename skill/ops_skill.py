from skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.goods_models import Goods
from common.logger import log_info, log_error

class CheckStockParams(SkillParams):
    goods_id: str
    num: int = Field(ge=1)

class ModifyStockParams(SkillParams):
    goods_id: str
    new_stock: int = Field(ge=0)

# 校验库存是否充足
class CheckStockSkill(BaseSkill):
    name = "check_goods_stock"
    description = "校验指定商品库存是否满足购买数量"
    params_model = CheckStockParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        goods_id = args.goods_id
        session_id = "stock_check"
        log_info(trace_id, session_id, f"执行工具{self.name}，goods_id={goods_id}, check_num={args.num}")
        try:
            goods = db.query(Goods).filter(Goods.id == args.goods_id).first()
            if not goods:
                log_info(trace_id, session_id, f"商品{goods_id}不存在")
                return {"code":-1, "msg":"商品不存在"}
            if goods.stock >= args.num:
                log_info(trace_id, session_id, f"商品{goods_id}库存充足，当前库存{goods.stock}")
                return {"code":0, "stock_enough": True, "current_stock": goods.stock}
            else:
                log_info(trace_id, session_id, f"商品{goods_id}库存不足，需求{args.num},库存{goods.stock}")
                return {"code":0, "stock_enough": False, "current_stock": goods.stock}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}库存校验异常，goods_id={goods_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 后台修改商品库存
class ModifyStockSkill(BaseSkill):
    name = "modify_goods_stock"
    description = "运营后台修改商品总库存数量"
    params_model = ModifyStockParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        goods_id = args.goods_id
        session_id = "stock_op"
        log_info(trace_id, session_id, f"执行工具{self.name}，goods_id={goods_id}, new_stock={args.new_stock}")
        try:
            goods = db.query(Goods).filter(Goods.id == args.goods_id).first()
            if not goods:
                log_info(trace_id, session_id, f"商品{goods_id}不存在")
                return {"code":-1, "msg":"商品不存在"}
            goods.stock = args.new_stock
            db.commit()
            log_info(trace_id, session_id, f"商品{goods_id}库存修改为{args.new_stock}")
            return {"code":0, "msg":"库存修改完成"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}修改库存异常，goods_id={goods_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

OPS_SKILL_CLS = [
    CheckStockSkill,
    ModifyStockSkill
]