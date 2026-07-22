from mcp_server.skill.base import SkillParams, BaseSkill
from database.db import SessionLocal
from db.admin_models import AdminSalesStat
from common.logger import log_info, log_error

class QueryDailySalesParams(SkillParams):
    start_date: str
    end_date: str

# 查询时间段销售统计报表
class QueryDailySalesSkill(BaseSkill):
    name = "query_daily_sales_stat"
    description = "查询区间内每日订单量、成交额、退款率报表"
    params_model = QueryDailySalesParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        start = args.start_date
        end = args.end_date
        session_id = "stat_query"
        log_info(trace_id, session_id, f"执行工具{self.name}，统计区间：{start} ~ {end}")
        try:
            stats = db.query(AdminSalesStat).filter(
                AdminSalesStat.stat_date >= args.start_date,
                AdminSalesStat.stat_date <= args.end_date
            ).all()
            arr = []
            for s in stats:
                arr.append({
                    "stat_date": s.stat_date,
                    "order_total": s.order_total,
                    "turnover": float(s.turnover),
                    "refund_rate": float(s.refund_rate)
                })
            log_info(trace_id, session_id, f"销售统计查询完成，共{len(arr)}天数据")
            return {"code":0, "sales_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}销售统计查询异常，区间{start}~{end}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

ADMIN_SKILL_CLS = [
    QueryDailySalesSkill
]