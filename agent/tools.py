from langchain_core.tools import tool
from vector_store.store import search_goods_vector
from sqlalchemy.orm import Session
from db.models import Goods
from database.db import SessionLocal

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
    goods = db.query(Goods).filter(Goods.id.in_(goods_id)).all()
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