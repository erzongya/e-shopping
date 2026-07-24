# app/api/schemas/goods.py
"""
商品相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 请求模型 ====================

class ListGoodsRequest(BaseModel):
    """商品列表筛选请求"""
    category: Optional[str] = Field(None, description="商品分类")
    sub_category: Optional[str] = Field(None, description="子分类")
    brand: Optional[str] = Field(None, description="品牌")
    min_price: Optional[float] = Field(None, description="最低价格")
    max_price: Optional[float] = Field(None, description="最高价格")
    is_flash: Optional[int] = Field(None, description="是否秒杀: 1是 0否")
    is_hot: Optional[bool] = Field(None, description="是否热卖")
    is_new: Optional[bool] = Field(None, description="是否新品")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


# ==================== 响应模型 ====================

class GoodsSpecResponse(BaseModel):
    """商品规格响应"""
    id: str
    spec_name: str
    spec_value: Optional[str]
    spec_price: float
    spec_stock: int


class GoodsDetailResponse(BaseModel):
    """商品详情响应"""
    id: str
    name: str
    category: str
    sub_category: Optional[str]
    brand: Optional[str]
    price: float
    flash_price: float
    stock: int
    sold_count: int
    desc: Optional[str]
    images: Optional[str]
    is_flash: int
    flash_limit: int
    buy_limit: int
    flash_end_time: Optional[str]
    is_hot: bool
    is_new: bool
    specs: List[GoodsSpecResponse] = []


class GoodsListItemResponse(BaseModel):
    """商品列表项响应"""
    id: str
    name: str
    category: str
    brand: Optional[str]
    price: float
    flash_price: float
    stock: int
    sold_count: int
    is_flash: int
    is_hot: bool
    is_new: bool


class GoodsListResponse(BaseModel):
    """商品列表响应"""
    list: List[GoodsListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GoodsCommentResponse(BaseModel):
    """商品评论响应"""
    id: str
    content: str
    score: int
    tag: Optional[str]
    images: Optional[str]
    created_at: str


class GoodsCategoryResponse(BaseModel):
    """商品分类响应"""
    id: str
    name: str
    level: int
    icon: Optional[str]
    children: List['GoodsCategoryResponse'] = []


# 处理循环引用
GoodsCategoryResponse.model_rebuild()