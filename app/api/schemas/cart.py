
"""
购物车相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ==================== 请求模型 ====================

class AddToCartRequest(BaseModel):
    """添加到购物车请求"""
    goods_id: str = Field(..., description="商品ID")
    quantity: int = Field(1, ge=1, description="数量")
    spec_id: Optional[str] = Field(None, description="规格ID")


class UpdateCartRequest(BaseModel):
    """更新购物车请求"""
    quantity: int = Field(..., ge=0, description="数量")


# ==================== 响应模型 ====================

class CartItemResponse(BaseModel):
    """购物车项响应"""
    id: str
    goods_id: str
    goods_name: str
    goods_image: Optional[str]
    spec_id: Optional[str]
    spec_name: Optional[str]
    price: float
    quantity: int
    total: float
    stock: int
    selected: bool


class CartListResponse(BaseModel):
    """购物车列表响应"""
    list: List[CartItemResponse]
    total_count: int
    total_amount: float
    selected_amount: float