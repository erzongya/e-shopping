"""
商品模块数据模型
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, SmallInteger, Boolean
from app.models.base import BaseModel


class Goods(BaseModel):
    __tablename__ = "goods"

    name = Column(String(255), nullable=False, comment="商品名称")
    category = Column(String(100), index=True, comment="商品分类")
    sub_category = Column(String(100), comment="子分类")
    brand = Column(String(100), comment="品牌")

    price = Column(Numeric(10, 2), nullable=False, comment="日常售价")
    flash_price = Column(Numeric(10, 2), default=0.00, comment="秒杀价")
    cost_price = Column(Numeric(10, 2), comment="成本价")

    stock = Column(Integer, nullable=False, default=0, comment="库存")
    sold_count = Column(Integer, default=0, comment="已售数量")
    view_count = Column(Integer, default=0, comment="浏览次数")

    desc = Column(Text, comment="商品详情")
    images = Column(Text, comment="图片列表JSON")
    video = Column(String(500), comment="视频URL")

    is_flash = Column(SmallInteger, default=0, comment="是否秒杀0否1是")
    flash_limit = Column(Integer, default=1, comment="秒杀限购")
    buy_limit = Column(Integer, default=99, comment="日常限购")
    flash_end_time = Column(DateTime, comment="秒杀结束时间")

    is_hot = Column(Boolean, default=False, comment="是否热卖")
    is_new = Column(Boolean, default=False, comment="是否新品")
    is_recommend = Column(Boolean, default=False, comment="是否推荐")

    status = Column(SmallInteger, default=1, comment="状态1上架2下架")


class GoodsSpec(BaseModel):
    __tablename__ = "goods_spec"

    goods_id = Column(String(64), nullable=False, index=True, comment="商品ID")
    spec_name = Column(String(100), comment="规格名称颜色/尺寸")
    spec_value = Column(String(100), comment="规格值红/L码")
    spec_price = Column(Numeric(10, 2), default=0.00, comment="规格加价")
    spec_stock = Column(Integer, default=0, comment="规格独立库存")
    spec_image = Column(String(500), comment="规格图片")


class GoodsComment(BaseModel):
    __tablename__ = "goods_comment"

    goods_id = Column(String(64), nullable=False, index=True, comment="商品ID")
    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    order_id = Column(String(64), comment="订单ID")

    content = Column(Text, comment="评价内容")
    images = Column(Text, comment="图片列表JSON")
    score = Column(SmallInteger, nullable=False, comment="评分1-5")
    tag = Column(String(50), comment="标签")

    reply_content = Column(Text, comment="商家回复")
    reply_time = Column(DateTime, comment="回复时间")

    is_anonymous = Column(Boolean, default=False, comment="是否匿名")
    status = Column(SmallInteger, default=1, comment="状态1显示2隐藏")


class GoodsCategory(BaseModel):
    __tablename__ = "goods_category"

    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(String(64), default="0", comment="父分类ID")
    level = Column(SmallInteger, default=1, comment="层级1-3")
    sort = Column(Integer, default=0, comment="排序权重")
    icon = Column(String(500), comment="分类图标")