"""
订单模块数据模型
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger,Boolean
from app.models.base import BaseModel


class Order(BaseModel):
    __tablename__ = "order"

    order_no = Column(String(32), unique=True, nullable=False, index=True, comment="订单号")
    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")

    total_amount = Column(Numeric(10, 2), nullable=False, comment="商品总金额")
    discount_amount = Column(Numeric(10, 2), default=0.00, comment="优惠金额")
    freight_amount = Column(Numeric(10, 2), default=0.00, comment="运费")
    pay_amount = Column(Numeric(10, 2), nullable=False, comment="实付金额")

    pay_method = Column(String(50), comment="支付方式wechat/alipay/balance")
    pay_time = Column(DateTime, comment="支付时间")
    pay_transaction_id = Column(String(100), comment="交易流水号")

    status = Column(SmallInteger, default=1, comment="状态1待支付2已支付3已发货4已完成5已取消6退款中7已退款")

    receiver_name = Column(String(50), nullable=False, comment="收货人")
    receiver_phone = Column(String(20), nullable=False, comment="收货手机")
    receiver_address = Column(String(500), nullable=False, comment="收货地址")
    receiver_province = Column(String(50), comment="省份")
    receiver_city = Column(String(50), comment="城市")
    receiver_district = Column(String(50), comment="区县")

    logistics_company = Column(String(100), comment="物流公司")
    logistics_no = Column(String(100), comment="物流单号")
    ship_time = Column(DateTime, comment="发货时间")
    confirm_time = Column(DateTime, comment="确认收货时间")

    user_remark = Column(String(500), comment="用户备注")
    admin_remark = Column(String(500), comment="管理员备注")
    cancel_time = Column(DateTime, comment="取消时间")
    cancel_reason = Column(String(500), comment="取消原因")


class OrderItem(BaseModel):
    __tablename__ = "order_item"

    order_id = Column(String(64), nullable=False, index=True, comment="订单ID")
    goods_id = Column(String(64), nullable=False, comment="商品ID")
    spec_id = Column(String(64), comment="规格ID")

    goods_name = Column(String(255), nullable=False, comment="商品名称快照")
    goods_image = Column(String(500), comment="商品图片快照")
    spec_name = Column(String(100), comment="规格名称快照")

    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    quantity = Column(Integer, nullable=False, comment="数量")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="小计")

    is_commented = Column(Boolean, default=False, comment="是否已评价")


class OrderLog(BaseModel):
    __tablename__ = "order_log"

    order_id = Column(String(64), nullable=False, index=True, comment="订单ID")
    operator = Column(String(64), comment="操作人ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    content = Column(String(500), comment="操作内容")
    before_status = Column(SmallInteger, comment="操作前状态")
    after_status = Column(SmallInteger, comment="操作后状态")