"""
售后模块数据模型
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger
from app.models.base import BaseModel


class AfterSale(BaseModel):
    __tablename__ = "aftersale"

    order_id = Column(String(64), nullable=False, index=True, comment="订单ID")
    order_item_id = Column(String(64), nullable=False, comment="订单明细ID")
    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")

    type = Column(SmallInteger, nullable=False, comment="类型1仅退款2退货退款")

    reason = Column(String(500), nullable=False, comment="申请原因")
    description = Column(Text, comment="详细描述")
    images = Column(Text, comment="凭证图片JSON")
    refund_amount = Column(Numeric(10, 2), nullable=False, comment="退款金额")

    return_logistics_company = Column(String(100), comment="退货物流公司")
    return_logistics_no = Column(String(100), comment="退货物流单号")
    return_receive_time = Column(DateTime, comment="商家收货时间")

    status = Column(SmallInteger, default=1, comment="状态1待审核2审核通过3审核拒绝4退货中5已完成6已关闭")

    audit_time = Column(DateTime, comment="审核时间")
    audit_remark = Column(String(500), comment="审核备注")
    reject_time = Column(DateTime, comment="拒绝时间")
    reject_reason = Column(String(500), comment="拒绝原因")

    complete_time = Column(DateTime, comment="完成时间")
    refund_time = Column(DateTime, comment="退款时间")
    refund_transaction_id = Column(String(100), comment="退款流水号")