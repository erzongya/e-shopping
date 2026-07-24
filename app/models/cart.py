"""
购物车模块数据模型
"""
from sqlalchemy import Column, String, Integer, Boolean
from app.models.base import BaseModel


class Cart(BaseModel):
    __tablename__ = "cart"

    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    goods_id = Column(String(64), nullable=False, comment="商品ID")
    spec_id = Column(String(64), comment="规格ID")
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    selected = Column(Boolean, default=True, comment="是否选中")