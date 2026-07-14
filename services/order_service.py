from sqlalchemy.orm import Session
from db.models import Order,Goods
from utils.logger import logger


def create_order(db:Session,user_id:str,goods_id:int,pay_price:float):
    """创建订单，自动校验商品库存"""
    goods = db.query(Goods).get(goods_id)
    if not goods or goods.stock <= 0:
        logger.warning(f"商品{goods_id}库存不足，下单失败")
        return None

    new_order = Order(
        user_id=user_id,
        goods_id=goods_id,
        origin_price=goods.price,
        real_pay=pay_price
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    logger.info(f"用户{user_id}创建订单成功，订单id：{new_order.id}")
    return new_order

def get_user_orders(db: Session, user_id: str):
    """查询用户全部历史订单"""
    return db.query(Order).filter(Order.user_id == user_id).all()