# 营销优惠券域
from sqlalchemy import Column, String, Integer, Numeric, DateTime, SmallInteger
from db.base import Base

class ActivityCoupon(Base):
    __tablename__ = "activity_coupon"
    id = Column(String(64), primary_key=True, comment="活动券ID")
    coupon_name = Column(String(100), nullable=False, comment="优惠券名称")
    full_limit = Column(Numeric(10, 2), default=0, comment="满减门槛")
    discount = Column(Numeric(10, 2), default=0, comment="减免金额")
    total_limit = Column(Integer, default=1000, comment="总发放上限")
    receive_count = Column(Integer, default=0, comment="已领取数量")
    expire_time = Column(DateTime, nullable=False, comment="过期时间")
    need_point = Column(Integer, default=0, comment="积分兑换所需积分，0=免费领取")


class UserCoupon(Base):
    __tablename__ = "user_coupon"
    id = Column(String(64), primary_key=True, comment="用户持有券ID")
    user_id = Column(String(64), nullable=False, comment="用户ID")
    activity_id = Column(String(64), nullable=False, comment="关联活动优惠券ID")
    is_used = Column(SmallInteger, default=0, comment="0未使用 1已使用")
    create_time = Column(DateTime)


class ActivityFlash(Base):
    __tablename__ = "activity_flash"
    id = Column(String(64), primary_key=True)
    goods_id = Column(String(64), nullable=False)
    flash_start = Column(DateTime)
    flash_end = Column(DateTime)
    stock_total = Column(Integer, default=0)