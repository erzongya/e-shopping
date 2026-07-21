#运营后台统计域
from sqlalchemy import Column, String, Integer, Numeric, DateTime
from db.base import Base

class AdminSalesStat(Base):
    __tablename__ = "admin_sales_stat"
    id = Column(String(64), primary_key=True)
    stat_date = Column(String(32), comment="统计日期 yyyy-MM-dd")
    order_total = Column(Integer, default=0, comment="当日订单总数")
    turnover = Column(Numeric(12, 2), default=0, comment="当日成交额")
    refund_rate = Column(Numeric(5, 2), default=0, comment="退款率")
    create_time = Column(DateTime)