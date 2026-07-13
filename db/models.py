from sqlalchemy import Column, Integer, String, Float, Text
from db.base import Base

class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    price = Column(Float)
    stock = Column(Integer)
    category = Column(String(50))
    desc = Column(Text)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50))
    goods_id = Column(Integer)
    real_price = Column(Float)
    status = Column(String(20), default="pending")