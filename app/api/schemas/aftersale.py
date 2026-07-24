# app/api/schemas/aftersale.py
"""
售后相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ==================== 请求模型 ====================

class ApplyRefundRequest(BaseModel):
    """申请售后请求"""
    order_id: str = Field(..., description="订单ID")
    order_item_id: str = Field(..., description="订单明细ID")
    type: int = Field(..., description="售后类型: 1仅退款 2退货退款")
    reason: str = Field(..., max_length=500, description="申请原因")
    description: Optional[str] = Field("", max_length=1000, description="详细描述")
    images: Optional[str] = Field("", description="凭证图片JSON")


# ==================== 响应模型 ====================

class AfterSaleResponse(BaseModel):
    """售后响应"""
    id: str
    order_id: str
    type: int
    type_name: str
    refund_amount: float
    status: int
    status_name: str
    reason: str
    description: Optional[str]
    images: Optional[str]
    audit_remark: Optional[str]
    reject_reason: Optional[str]
    return_logistics_company: Optional[str]
    return_logistics_no: Optional[str]
    created_at: str


class AfterSaleListItemResponse(BaseModel):
    """售后列表项响应"""
    id: str
    order_id: str
    type: int
    type_name: str
    refund_amount: float
    status: int
    status_name: str
    created_at: str