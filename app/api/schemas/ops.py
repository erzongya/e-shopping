
"""
运营相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ==================== 请求模型 ====================

class SalesReportRequest(BaseModel):
    """销售报表请求"""
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")


# ==================== 响应模型 ====================

class DailySalesResponse(BaseModel):
    """每日销售数据响应"""
    date: str
    order_count: int
    turnover: float
    avg_order_amount: float


class SalesSummaryResponse(BaseModel):
    """销售汇总响应"""
    total_orders: int
    total_turnover: float
    total_refund: float
    total_users: int
    avg_order_amount: float


class SalesReportResponse(BaseModel):
    """销售报表响应"""
    summary: SalesSummaryResponse
    daily_data: List[DailySalesResponse]
    category_stats: List[dict]
    start_date: str
    end_date: str


class DashboardStatsResponse(BaseModel):
    """仪表盘数据响应"""
    today: dict
    month: dict
    yesterday: dict
    trend: List[dict]
    top_products: List[dict]
    update_time: str


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int
    active_users: int
    vip_users: int
    today_new: int
    active_rate: float


class GoodsStatsResponse(BaseModel):
    """商品统计响应"""
    total_goods: int
    on_sale: int
    low_stock: int
    out_of_stock: int


class OrderStatsResponse(BaseModel):
    """订单统计响应"""
    pending: int
    today_orders: int
    status_stats: List[dict]