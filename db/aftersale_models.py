# 售后工单域
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger
from db.base import Base

class OrderRefund(Base):
    __tablename__ = "order_refund"
    id = Column(String(64), primary_key=True, comment="退款工单ID")
    user_id = Column(String(64), nullable=False, comment="操作用户ID")
    order_id = Column(String(64), nullable=False, comment="关联订单ID")
    refund_type = Column(String(32), nullable=False, comment="only_refund仅退款 / return_refund退货退款")
    reason = Column(Text, comment="退款申请原因")
    refund_amount = Column(Numeric(10, 2), nullable=False, comment="退款金额")
    status = Column(String(32), default="pending", comment="pending待审核 / pass通过 / reject驳回")
    create_time = Column(DateTime)


class ComplaintTicket(Base):
    __tablename__ = "complaint_ticket"
    id = Column(String(64), primary_key=True, comment="投诉工单ID")
    user_id = Column(String(64), nullable=False, comment="投诉用户ID")
    order_id = Column(String(64), nullable=False, comment="关联订单ID")
    complaint_type = Column(String(32), nullable=False, comment="破损/错发/发货慢/假货/服务差")
    description = Column(Text, comment="投诉详细描述")
    status = Column(String(32), default="pending")
    create_time = Column(DateTime)


class ManualTicket(Base):
    __tablename__ = "manual_ticket"
    id = Column(String(64), primary_key=True, comment="人工客服排队工单ID")
    user_id = Column(String(64), nullable=False, comment="用户ID")
    session_id = Column(String(128), nullable=False, comment="对话会话ID")
    status = Column(String(32), default="wait", comment="wait排队 / online已接入 / close会话结束")
    create_time = Column(DateTime)