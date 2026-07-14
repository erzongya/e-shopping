from langchain_core.tools import tool
from vector_store.store import search_goods_vector
from sqlalchemy.orm import Session
from db.models import Goods,Order
from database.db import SessionLocal
import datetime
@tool
def search_similar_goods(query: str,top_k: int = 3) -> list[str]:
    """
    根据用户自然语言描述，语义检索相似商品ID
    :param query: 用户查询描述
    :param top_k: 返回匹配商品数量
    :return: 匹配商品id列表
    """
    res = search_goods_vector(query,top_k)
    ids = res['ids'][0]
    return ids

@tool
def get_goods_detail(goods_id: str) ->  list[dict]:
    """
    根据商品ID列表，查询完整商品详情
    Args:
        goods_id_list: 商品id数组
    Return:
        商品完整信息字典列表
    """
    db:Session = SessionLocal()
    goods = db.query(Goods).filter(Goods.id == (goods_id)).all()
    db.close()
    return [
        {
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "price": g.price,
            "stock": g.stock,
            "desc": g.desc
        }
        for g in goods
    ]
@tool
def filter_goods(goods_list: list[dict], min_price: float = None, max_price: float = None, only_in_stock: bool = True) -> list[dict]:
    """
    拿到商品列表后，按预算、库存过滤商品
    :param goods_list: get_goods_detail返回的完整商品数组
    :param min_price: 最低预算，不传不限
    :param max_price: 最高预算，不传不限
    :param only_in_stock: 是否只保留有库存商品，默认True过滤缺货
    :return: 过滤后的商品列表
    """
    res = []
    for item in goods_list:
        #过滤缺货
        if only_in_stock and item["stock"] <= 0:
            continue
        # 价格下限
        if min_price is not  None and item["price"] < min_price:
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        res.append(item)
    return res
@tool
def query_order(order_no: str) -> dict:
    """
    用户查询订单、咨询订单金额/状态时调用
    :param order_no: 用户提供的订单号（订单id）
    :return: 订单完整信息，无订单返回空字典
    """
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_no).first()
    db.close()
    if not order:
        return {}
    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "goods_id": order.goods_id,
        "origin_price": float(order.origin_price),
        "real_pay": float(order.real_pay),
        "status": order.status
    }
@tool
def check_return_eligibility(order_no: str) -> str:
    """
    用户申请退货时调用，校验是否满足退货资格
    :param order_no: 订单号
    :return: 资格说明文本
    """
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_no).first()
    db.close()
    if not order:
        return "未查询到该订单，无法申请退货"
    if order.status == "refund":
        return "该订单已完成退款，请勿重复申请"
    if order.status == "pending":
        return "订单尚未支付，无需申请退货"
    return "符合退货条件，可以提交退货申请"