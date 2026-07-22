from mcp_server.skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.cart_models import UserCart
from db.goods_models import Goods
import uuid
from datetime import datetime
from common.logger import log_info, log_error

class GetUserCartParams(SkillParams):
    user_id: str

class AddCartItemParams(SkillParams):
    user_id: str
    goods_id: str
    spec_id: str | None = None
    buy_num: int = Field(ge=1, default=1)

class UpdateCartNumParams(SkillParams):
    cart_id: str
    buy_num: int = Field(ge=1)

class DeleteCartParams(SkillParams):
    cart_id: str

# 查询用户购物车
class GetUserCartSkill(BaseSkill):
    name = "get_user_cart"
    description = "查询用户全部购物车商品，关联商品名称、单价"
    params_model = GetUserCartParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}")
        try:
            rows = db.query(UserCart, Goods)\
                .join(Goods, UserCart.goods_id == Goods.id)\
                .filter(UserCart.user_id == args.user_id).all()
            arr = []
            for cart, goods in rows:
                arr.append({
                    "cart_id": cart.id,
                    "goods_id": goods.id,
                    "goods_name": goods.name,
                    "price": float(goods.price),
                    "buy_num": cart.buy_num,
                    "checked": cart.is_checked
                })
            log_info(trace_id, session_id, f"用户{user_id}购物车查询完成，共{len(arr)}条")
            return {"code":0, "cart_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询购物车异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 加入购物车
class AddCartItemSkill(BaseSkill):
    name = "add_cart_item"
    description = "商品加入购物车，校验库存是否充足"
    params_model = AddCartItemParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        user_id = args.user_id
        session_id = user_id
        log_info(trace_id, session_id, f"执行工具{self.name}，user_id={user_id}, goods_id={args.goods_id}")
        try:
            goods = db.query(Goods).filter(Goods.id == args.goods_id).first()
            if not goods:
                log_info(trace_id, session_id, f"商品{args.goods_id}不存在")
                return {"code":-1, "msg":"商品不存在"}
            if goods.stock < args.buy_num:
                log_info(trace_id, session_id, f"商品库存不足，需求{args.buy_num},库存{goods.stock}")
                return {"code":-1, "msg":"库存不足"}
            cart = UserCart(
                id=str(uuid.uuid4()),
                user_id=args.user_id,
                goods_id=args.goods_id,
                spec_id=args.spec_id,
                buy_num=args.buy_num,
                is_checked=0,
                create_time=datetime.now()
            )
            db.add(cart)
            db.commit()
            log_info(trace_id, session_id, f"商品{args.goods_id}加入购物车成功")
            return {"code":0, "msg":"加入购物车成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}加购异常，user_id={user_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 修改购物车数量
class UpdateCartNumSkill(BaseSkill):
    name = "update_cart_num"
    description = "修改购物车内商品购买数量"
    params_model = UpdateCartNumParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        cart_id = args.cart_id
        session_id = "cart_op"
        log_info(trace_id, session_id, f"执行工具{self.name}，cart_id={cart_id}, new_num={args.buy_num}")
        try:
            cart = db.query(UserCart).filter(UserCart.id == args.cart_id).first()
            if not cart:
                log_info(trace_id, session_id, f"购物车条目{cart_id}不存在")
                return {"code":-1, "msg":"购物车条目不存在"}
            cart.buy_num = args.buy_num
            db.commit()
            log_info(trace_id, session_id, f"购物车{cart_id}数量修改完成")
            return {"code":0, "msg":"修改数量成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}修改购物车数量异常，cart_id={cart_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# 删除购物车条目
class DeleteCartSkill(BaseSkill):
    name = "delete_cart_item"
    description = "删除一条购物车商品"
    params_model = DeleteCartParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        cart_id = args.cart_id
        session_id = "cart_op"
        log_info(trace_id, session_id, f"执行工具{self.name}，cart_id={cart_id}")
        try:
            cart = db.query(UserCart).filter(UserCart.id == args.cart_id).first()
            if not cart:
                log_info(trace_id, session_id, f"购物车条目{cart_id}不存在")
                return {"code":-1, "msg":"条目不存在"}
            db.delete(cart)
            db.commit()
            log_info(trace_id, session_id, f"购物车{cart_id}删除成功")
            return {"code":0, "msg":"删除成功"}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}删除购物车异常，cart_id={cart_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

CART_SKILL_CLS = [
    GetUserCartSkill,
    AddCartItemSkill,
    UpdateCartNumSkill,
    DeleteCartSkill
]