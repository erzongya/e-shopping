from sqlalchemy.orm import Session
from database.db import get_db
from db.models import Goods

def get_goods_by_id(db: Session, goods_id: int):
    """根据商品ID查询单品详情"""
    return db.query(Goods).filter(Goods.id == goods_id).first()

def search_goods_by_keyword(db: Session, keyword: str):
    """数据库模糊关键词检索商品"""
    return db.query(Goods).filter(Goods.name.like(f"%{keyword}%")).all()

def get_all_goods(db: Session):
    """获取全部商品，用于批量向量入库"""
    return db.query(Goods).all()
