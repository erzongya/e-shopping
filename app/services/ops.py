"""
运营业务逻辑服务 - 异步版
包含：仪表盘数据、销售报表、用户统计、商品统计等
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, extract
from datetime import datetime, timedelta

from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.goods import Goods
from app.models.aftersale import AfterSale
from app.common.exceptions import BusinessException


class AsyncOpsService:
    """运营业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 仪表盘数据 ==========

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取运营仪表盘统计数据"""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        month_start = datetime(today.year, today.month, 1)

        today_stats = await self._get_today_stats(today_start, today_end)
        month_stats = await self._get_month_stats(month_start, today_end)
        yesterday_stats = await self._get_yesterday_stats(today)
        trend_data = await self._get_trend_data(days=7)
        top_products = await self._get_top_products(limit=10)

        return {
            "today": today_stats,
            "month": month_stats,
            "yesterday": yesterday_stats,
            "trend": trend_data,
            "top_products": top_products,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    async def _get_today_stats(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取今日统计数据"""
        result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        order_count = result.scalar() or 0

        result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        turnover = result.scalar() or 0

        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.register_time >= start,
                User.register_time <= end
            )
        )
        new_users = result.scalar() or 0

        result = await self.db.execute(
            select(func.sum(AfterSale.refund_amount)).where(
                AfterSale.created_at >= start,
                AfterSale.created_at <= end,
                AfterSale.status == 5
            )
        )
        refund_amount = result.scalar() or 0

        return {
            "order_count": order_count,
            "turnover": round(float(turnover), 2),
            "new_users": new_users,
            "refund_amount": round(float(refund_amount), 2)
        }

    async def _get_month_stats(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取本月统计数据"""
        result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        order_count = result.scalar() or 0

        result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        turnover = result.scalar() or 0

        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.register_time >= start,
                User.register_time <= end
            )
        )
        new_users = result.scalar() or 0

        result = await self.db.execute(
            select(func.sum(AfterSale.refund_amount)).where(
                AfterSale.created_at >= start,
                AfterSale.created_at <= end,
                AfterSale.status == 5
            )
        )
        refund_amount = result.scalar() or 0

        return {
            "order_count": order_count,
            "turnover": round(float(turnover), 2),
            "new_users": new_users,
            "refund_amount": round(float(refund_amount), 2)
        }

    async def _get_yesterday_stats(self, today: datetime.date) -> Dict[str, Any]:
        """获取昨日统计数据"""
        yesterday = today - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())

        result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= yesterday_start,
                Order.created_at <= yesterday_end,
                Order.status >= 2
            )
        )
        order_count = result.scalar() or 0

        result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                Order.created_at >= yesterday_start,
                Order.created_at <= yesterday_end,
                Order.status >= 2
            )
        )
        turnover = result.scalar() or 0

        return {
            "order_count": order_count,
            "turnover": round(float(turnover), 2),
            "date": yesterday.strftime("%Y-%m-%d")
        }

    async def _get_trend_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取近N天趋势数据"""
        result = []
        today = datetime.now().date()

        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            order_result = await self.db.execute(
                select(func.count(Order.id)).where(
                    Order.created_at >= start,
                    Order.created_at <= end,
                    Order.status >= 2
                )
            )
            order_count = order_result.scalar() or 0

            turnover_result = await self.db.execute(
                select(func.sum(Order.pay_amount)).where(
                    Order.created_at >= start,
                    Order.created_at <= end,
                    Order.status >= 2
                )
            )
            turnover = turnover_result.scalar() or 0

            result.append({
                "date": date.strftime("%Y-%m-%d"),
                "order_count": order_count,
                "turnover": round(float(turnover), 2)
            })

        return result

    async def _get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热销商品排行"""
        result = await self.db.execute(
            select(
                OrderItem.goods_id,
                OrderItem.goods_name,
                func.sum(OrderItem.quantity).label("total_quantity"),
                func.sum(OrderItem.total_amount).label("total_amount")
            ).where(
                OrderItem.is_commented == True
            ).group_by(
                OrderItem.goods_id,
                OrderItem.goods_name
            ).order_by(
                desc("total_amount")
            ).limit(limit)
        )
        rows = result.all()

        return [{
            "goods_id": r.goods_id,
            "goods_name": r.goods_name,
            "total_quantity": r.total_quantity,
            "total_amount": round(float(r.total_amount), 2)
        } for r in rows]

    # ========== 销售报表 ==========

    async def get_sales_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取销售报表"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

        daily_data = await self._get_daily_sales(start, end)
        summary = await self._get_sales_summary(start, end)
        category_stats = await self._get_category_stats(start, end)

        return {
            "summary": summary,
            "daily_data": daily_data,
            "category_stats": category_stats,
            "start_date": start_date,
            "end_date": end_date
        }

    async def _get_daily_sales(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """获取每日销售明细"""
        result = await self.db.execute(
            select(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.pay_amount).label("turnover"),
                func.avg(Order.pay_amount).label("avg_order_amount")
            ).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            ).group_by(
                func.date(Order.created_at)
            ).order_by(
                func.date(Order.created_at)
            )
        )
        rows = result.all()

        return [{
            "date": r.date.strftime("%Y-%m-%d") if r.date else None,
            "order_count": r.order_count,
            "turnover": round(float(r.turnover), 2) if r.turnover else 0,
            "avg_order_amount": round(float(r.avg_order_amount), 2) if r.avg_order_amount else 0
        } for r in rows]

    async def _get_sales_summary(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取销售汇总"""
        order_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        total_orders = order_result.scalar() or 0

        turnover_result = await self.db.execute(
            select(func.sum(Order.pay_amount)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            )
        )
        total_turnover = turnover_result.scalar() or 0

        refund_result = await self.db.execute(
            select(func.sum(AfterSale.refund_amount)).where(
                AfterSale.created_at >= start,
                AfterSale.created_at <= end,
                AfterSale.status == 5
            )
        )
        total_refund = refund_result.scalar() or 0

        user_result = await self.db.execute(
            select(func.count(User.id)).where(
                User.register_time >= start,
                User.register_time <= end
            )
        )
        total_users = user_result.scalar() or 0

        avg_order = total_turnover / total_orders if total_orders > 0 else 0

        return {
            "total_orders": total_orders,
            "total_turnover": round(float(total_turnover), 2),
            "total_refund": round(float(total_refund), 2),
            "total_users": total_users,
            "avg_order_amount": round(float(avg_order), 2)
        }

    async def _get_category_stats(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """获取分类销售统计"""
        result = await self.db.execute(
            select(
                Goods.category,
                func.count(OrderItem.id).label("item_count"),
                func.sum(OrderItem.total_amount).label("total_amount")
            ).join(
                OrderItem, OrderItem.goods_id == Goods.id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status >= 2
            ).group_by(
                Goods.category
            ).order_by(
                desc("total_amount")
            ).limit(10)
        )
        rows = result.all()

        return [{
            "category": r.category or "未分类",
            "item_count": r.item_count,
            "total_amount": round(float(r.total_amount), 2) if r.total_amount else 0
        } for r in rows]

    # ========== 用户统计 ==========

    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计数据"""
        total_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0

        active_result = await self.db.execute(
            select(func.count(User.id)).where(
                User.status == 1,
                User.last_login_time >= datetime.now() - timedelta(days=30)
            )
        )
        active_users = active_result.scalar() or 0

        vip_result = await self.db.execute(
            select(func.count(User.id)).where(User.vip_level > 1)
        )
        vip_users = vip_result.scalar() or 0

        today_start = datetime.combine(datetime.now().date(), datetime.min.time())
        new_result = await self.db.execute(
            select(func.count(User.id)).where(User.register_time >= today_start)
        )
        today_new = new_result.scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "vip_users": vip_users,
            "today_new": today_new,
            "active_rate": round(active_users / total_users * 100, 2) if total_users > 0 else 0
        }

    # ========== 商品统计 ==========

    async def get_goods_stats(self) -> Dict[str, Any]:
        """获取商品统计数据"""
        total_result = await self.db.execute(select(func.count(Goods.id)))
        total_goods = total_result.scalar() or 0

        on_sale_result = await self.db.execute(
            select(func.count(Goods.id)).where(Goods.status == 1)
        )
        on_sale = on_sale_result.scalar() or 0

        low_stock_result = await self.db.execute(
            select(func.count(Goods.id)).where(
                Goods.stock < 10,
                Goods.stock > 0,
                Goods.status == 1
            )
        )
        low_stock = low_stock_result.scalar() or 0

        out_of_stock_result = await self.db.execute(
            select(func.count(Goods.id)).where(Goods.stock == 0)
        )
        out_of_stock = out_of_stock_result.scalar() or 0

        return {
            "total_goods": total_goods,
            "on_sale": on_sale,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        }

    # ========== 订单统计 ==========

    async def get_order_stats(self) -> Dict[str, Any]:
        """获取订单统计数据"""
        result = await self.db.execute(
            select(
                Order.status,
                func.count(Order.id).label("count")
            ).group_by(Order.status)
        )
        status_rows = result.all()
        status_stats = [{"status": r.status, "count": r.count} for r in status_rows]

        pending_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.status.in_([1, 2]))
        )
        pending = pending_result.scalar() or 0

        today_start = datetime.combine(datetime.now().date(), datetime.min.time())
        today_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.created_at >= today_start)
        )
        today_orders = today_result.scalar() or 0

        return {
            "pending": pending,
            "today_orders": today_orders,
            "status_stats": status_stats
        }

    # ========== 导出报表 ==========

    async def export_sales_report(self, start_date: str, end_date: str, format: str = "excel") -> Dict[str, Any]:
        """导出销售报表"""
        report_data = await self.get_sales_report(start_date, end_date)

        file_name = f"sales_report_{start_date}_{end_date}.{format}"
        file_path = f"/tmp/{file_name}"

        return {
            "file_name": file_name,
            "file_path": file_path,
            "data_count": len(report_data.get("daily_data", [])),
            "total_turnover": report_data.get("summary", {}).get("total_turnover", 0)
        }