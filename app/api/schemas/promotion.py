# app/api/schemas/promotion.py
"""
促销相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 请求模型 ====================

class CalculateDiscountRequest(BaseModel):
    """计算优惠请求"""
    amount: float = Field(..., description="订单金额")
    promotion_id: str = Field(..., description="促销活动ID")


class ReceiveCouponRequest(BaseModel):
    """领取优惠券请求"""
    coupon_id: str = Field(..., description="优惠券ID")


# ==================== 响应模型 ====================

class PromotionResponse(BaseModel):
    """促销活动响应"""
    id: str
    name: str
    type: int
    type_name: str
    min_amount: float
    discount_amount: float
    discount_rate: float
    start_time: str
    end_time: str


class DiscountResultResponse(BaseModel):
    """优惠计算结果响应"""
    promotion_id: str
    promotion_name: str
    original_amount: float
    discount_amount: float
    final_amount: float


class CouponResponse(BaseModel):
    """优惠券响应"""
    id: str
    name: str
    code: str
    type: int
    type_name: str
    min_amount: float
    discount_amount: float
    discount_rate: float
    max_discount: float
    start_time: str
    end_time: str
    remaining: int


class UserCouponResponse(BaseModel):
    """用户优惠券响应"""
    id: str
    coupon_id: str
    coupon_name: str
    type: int
    type_name: str
    min_amount: float
    discount_amount: float
    status: int
    status_name: str
    expire_time: str