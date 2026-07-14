# 导入sqlalchemy字段类型
from sqlalchemy import Column, Integer, String, Float, Text,Numeric
# 导入上面定义的全局基类
from db.base import Base

# 商品数据表
class Goods(Base):
    # 指定数据库内表名
    __tablename__ = "goods"
    # 主键自增ID，商品唯一标识
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 商品名称，字符串，非空
    name = Column(String(100), nullable=False)
    # 商品价格，浮点型
    price = Column(Numeric(10,2), nullable=False)
    # 库存数量
    stock = Column(Integer, nullable=False)
    # 商品分类：数码/服饰等
    category = Column(String(50))
    # 商品详情长文本描述
    desc = Column(Text)

# 订单数据表
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户唯一ID，区分不同下单用户
    user_id = Column(String(64))
    # 关联商品ID，外键逻辑（简易项目不做外键约束，简化开发）
    goods_id = Column(Integer)
    # 商品原价
    origin_price = Column(Numeric(10,2))
    # 使用优惠券后实付价格
    real_pay = Column(Numeric(10,2))
    # 订单状态：pending待支付 / paid已支付 / refund退款
    status = Column(String(20), default="pending")