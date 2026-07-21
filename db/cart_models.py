# 购物车域
from sqlalchemy import Column, String, Integer, DateTime, SmallInteger
from db.base import Base

class UserCart(Base):
    __tablename__ = "user_cart"
    id = Column(String(64), primary_key=True, comment="购物车条目ID")
    user_id = Column(String(64), nullable=False, comment="所属用户ID")
    goods_id = Column(String(64), nullable=False, comment="商品ID")
    spec_id = Column(String(64), comment="商品规格ID")
    buy_num = Column(Integer, default=1, comment="选购数量")
    is_checked = Column(SmallInteger, default=0, comment="结算勾选 0未选 1选中")
    create_time = Column(DateTime)