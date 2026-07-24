"""
运营 MCP 技能 - 异步版
"""
from typing import Dict, Any
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.ops import AsyncOpsService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class GetDashboardStatsParams(SkillParams):
    """获取仪表盘数据参数"""
    pass


class GetSalesReportParams(SkillParams):
    """获取销售报表参数"""
    start_date: str = Field(description="开始日期 YYYY-MM-DD")
    end_date: str = Field(description="结束日期 YYYY-MM-DD")


class GetUserStatsParams(SkillParams):
    """获取用户统计参数"""
    pass


class GetGoodsStatsParams(SkillParams):
    """获取商品统计参数"""
    pass


class GetOrderStatsParams(SkillParams):
    """获取订单统计参数"""
    pass


class ExportSalesReportParams(SkillParams):
    """导出销售报表参数"""
    start_date: str = Field(description="开始日期 YYYY-MM-DD")
    end_date: str = Field(description="结束日期 YYYY-MM-DD")
    format: str = Field("excel", description="导出格式: excel/pdf/csv")


# ========== 技能实现 ==========

class GetDashboardStatsSkill(BaseSkill):
    """获取仪表盘数据"""
    name = "get_dashboard_stats"
    description = "获取运营仪表盘统计数据，包含今日、本月、趋势、热销商品等"
    params_model = GetDashboardStatsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "dashboard", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.get_dashboard_stats()
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "dashboard", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetSalesReportSkill(BaseSkill):
    """获取销售报表"""
    name = "get_sales_report"
    description = "获取指定时间范围的销售报表，含每日明细和汇总"
    params_model = GetSalesReportParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "sales_report", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.get_sales_report(
                    start_date=args.start_date,
                    end_date=args.end_date
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "sales_report", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetUserStatsSkill(BaseSkill):
    """获取用户统计"""
    name = "get_user_stats"
    description = "获取用户统计数据，包含总数、活跃、VIP、新增等"
    params_model = GetUserStatsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "user_stats", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.get_user_stats()
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "user_stats", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetGoodsStatsSkill(BaseSkill):
    """获取商品统计"""
    name = "get_goods_stats"
    description = "获取商品统计数据，包含总数、上架、库存预警等"
    params_model = GetGoodsStatsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "goods_stats", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.get_goods_stats()
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "goods_stats", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetOrderStatsSkill(BaseSkill):
    """获取订单统计"""
    name = "get_order_stats"
    description = "获取订单统计数据，包含各状态数量、待处理等"
    params_model = GetOrderStatsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "order_stats", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.get_order_stats()
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "order_stats", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ExportSalesReportSkill(BaseSkill):
    """导出销售报表"""
    name = "export_sales_report"
    description = "导出销售报表，支持 excel/pdf/csv 格式"
    params_model = ExportSalesReportParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "export", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncOpsService(db)
                result = await service.export_sales_report(
                    start_date=args.start_date,
                    end_date=args.end_date,
                    format=args.format
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "export", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

OPS_SKILL_CLS = [
    GetDashboardStatsSkill,
    GetSalesReportSkill,
    GetUserStatsSkill,
    GetGoodsStatsSkill,
    GetOrderStatsSkill,
    ExportSalesReportSkill
]