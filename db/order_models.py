# 订单 & 物流域
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger
from db.base import Base

class UserOrder(Base):
    __tablename__ = "user_order"
    id = Column(String(64), primary_key=True, comment="订单主键ID")
    user_id = Column(String(64), nullable=False, comment="下单用户ID")
    goods_id = Column(String(64), nullable=False, comment="购买商品ID")
    spec_id = Column(String(64), comment="商品规格ID")
    order_no = Column(String(64), unique=True, nullable=False, comment="外部业务订单号")
    buy_num = Column(Integer, default=1, comment="购买件数")
    pay_price = Column(Numeric(10, 2), nullable=False, comment="实付金额")
    status = Column(String(32), nullable=False, comment="待付款/待发货/运输中/已完成/退款中/已取消")
    tracking_no = Column(String(64), comment="快递单号")
    create_time = Column(DateTime)


class OrderLogistics(Base):
    __tablename__ = "order_logistics"
    id = Column(String(64), primary_key=True)
    tracking_no = Column(String(64), nullable=False, comment="快递单号")
    track_time = Column(DateTime, comment="物流节点时间")
    track_info = Column(Text, comment="物流节点详情")