# models/promotion.py
"""
促销模块数据模型
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger, Boolean
from app.models.base import BaseModel


class Promotion(BaseModel):
    __tablename__ = "promotion"

    name = Column(String(200), nullable=False, comment="活动名称")
    type = Column(SmallInteger, nullable=False, comment="类型1满减2折扣3秒杀4优惠券")

    min_amount = Column(Numeric(10, 2), default=0.00, comment="满减门槛")
    discount_amount = Column(Numeric(10, 2), default=0.00, comment="减免金额")
    discount_rate = Column(Numeric(3, 2), default=1.00, comment="折扣率")

    apply_type = Column(SmallInteger, default=1, comment="适用类型1全部2指定分类3指定商品")
    apply_targets = Column(Text, comment="适用目标ID列表JSON")

    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")

    status = Column(SmallInteger, default=1, comment="状态1未开始2进行中3已结束4已禁用")


class Coupon(BaseModel):
    __tablename__ = "coupon"

    name = Column(String(200), nullable=False, comment="优惠券名称")
    code = Column(String(50), unique=True, index=True, comment="券码")

    type = Column(SmallInteger, default=1, comment="类型1满减券2折扣券")

    min_amount = Column(Numeric(10, 2), default=0.00, comment="使用门槛")
    discount_amount = Column(Numeric(10, 2), default=0.00, comment="减免金额")
    discount_rate = Column(Numeric(3, 2), default=1.00, comment="折扣率")
    max_discount = Column(Numeric(10, 2), default=0.00, comment="最大减免")

    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")

    stock = Column(Integer, default=0, comment="库存")
    limit_per_user = Column(Integer, default=1, comment="每人限领")
    used_count = Column(Integer, default=0, comment="已使用")

    status = Column(SmallInteger, default=1, comment="状态1有效2已停用")


class UserCoupon(BaseModel):
    __tablename__ = "user_coupon"

    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    coupon_id = Column(String(64), nullable=False, comment="优惠券ID")

    status = Column(SmallInteger, default=1, comment="状态1未使用2已使用3已过期")
    use_time = Column(DateTime, comment="使用时间")
    order_id = Column(String(64), comment="订单ID")