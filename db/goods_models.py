# 商品域
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger
from db.base import Base

class Goods(Base):
    __tablename__ = "goods"
    id = Column(String(64), primary_key=True, comment="商品唯一ID")
    name = Column(String(255), nullable=False, comment="商品名称")
    category = Column(String(100), comment="商品分类")
    price = Column(Numeric(10, 2), nullable=False, comment="日常售价")
    flash_price = Column(Numeric(10, 2), default=0.00, comment="秒杀价")
    stock = Column(Integer, nullable=False, default=0, comment="库存数量")
    desc = Column(Text, comment="商品详情描述")
    is_flash = Column(SmallInteger, default=0, comment="是否秒杀商品 0=否 1=是")
    flash_limit = Column(Integer, default=1, comment="秒杀单人限购件数")
    buy_limit = Column(Integer, default=99, comment="日常单人每日限购")
    flash_end_time = Column(DateTime, comment="秒杀活动结束时间")


class GoodsComment(Base):
    __tablename__ = "goods_comment"
    id = Column(String(64), primary_key=True, comment="评论ID")
    goods_id = Column(String(64), nullable=False, comment="关联商品ID")
    content = Column(Text, comment="评价正文")
    tag = Column(String(50), comment="标签：质量/物流/性价比")
    score = Column(SmallInteger, comment="评分1-5")
    create_time = Column(DateTime, comment="评价时间")


class GoodsSpec(Base):
    __tablename__ = "goods_spec"
    id = Column(String(64), primary_key=True, comment="规格ID")
    goods_id = Column(String(64), nullable=False, comment="商品ID")
    spec_name = Column(String(100), comment="规格名称（颜色/尺寸）")
    spec_price = Column(Numeric(10, 2), default=0.00, comment="规格加价")
    spec_stock = Column(Integer, default=0, comment="规格独立库存")