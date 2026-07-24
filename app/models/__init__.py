# app/models/__init__.py
"""
数据模型统一导出
"""
from app.models.base import Base, BaseModel
from app.models.user import User, UserAddress
from app.models.goods import Goods, GoodsSpec, GoodsComment, GoodsCategory
from app.models.order import Order, OrderItem, OrderLog
from app.models.cart import Cart
from app.models.promotion import Promotion, Coupon, UserCoupon
from app.models.aftersale import AfterSale
from app.models.admin import Admin, AdminLog
from app.models.chat import ChatSession, ChatHistory

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "UserAddress",
    "Goods",
    "GoodsSpec",
    "GoodsComment",
    "GoodsCategory",
    "Order",
    "OrderItem",
    "OrderLog",
    "Cart",
    "Promotion",
    "Coupon",
    "UserCoupon",
    "AfterSale",
    "Admin",
    "AdminLog",
    "ChatSession",
    "ChatHistory",
]