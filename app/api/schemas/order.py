
"""
订单相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 请求模型 ====================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    address_id: str = Field(..., description="收货地址ID")
    cart_ids: List[str] = Field(..., description="购物车ID列表")
    remark: Optional[str] = Field("", max_length=500, description="用户备注")


class PayOrderRequest(BaseModel):
    """支付订单请求"""
    pay_method: str = Field("balance", description="支付方式: balance/wechat/alipay")


class CancelOrderRequest(BaseModel):
    """取消订单请求"""
    reason: Optional[str] = Field("", max_length=500, description="取消原因")


# ==================== 响应模型 ====================

class OrderItemResponse(BaseModel):
    """订单明细响应"""
    id: str
    goods_name: str
    goods_image: Optional[str]
    spec_name: Optional[str]
    price: float
    quantity: int
    total_amount: float
    is_commented: bool


class OrderDetailResponse(BaseModel):
    """订单详情响应"""
    id: str
    order_no: str
    total_amount: float
    discount_amount: float
    freight_amount: float
    pay_amount: float
    status: int
    status_name: str
    pay_method: Optional[str]
    pay_time: Optional[str]
    logistics_company: Optional[str]
    logistics_no: Optional[str]
    ship_time: Optional[str]
    confirm_time: Optional[str]
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    user_remark: Optional[str]
    created_at: str
    items: List[OrderItemResponse]


class OrderListItemResponse(BaseModel):
    """订单列表项响应"""
    id: str
    order_no: str
    pay_amount: float
    status: int
    status_name: str
    created_at: str


class OrderListResponse(BaseModel):
    """订单列表响应"""
    list: List[OrderListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int