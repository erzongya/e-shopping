# 导入引擎、会话生成工具
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# 读取环境变量里的数据库连接地址
from config.settings import settings

# 导入ORM基类 + 全部分模块模型（路径对应你项目目录 db/xxx_models.py）
from db.base import Base
from db.goods_models import *
from db.user_models import *
from db.cart_models import *
from db.promoption_models import *
from db.order_models import *
from db.aftersale_models import *
from db.admin_models import *

# 1. 创建数据库引擎，读取.env中的DB_URL
engine = create_engine(
    settings.DB_URL,
    # SQLite专属参数，解决多线程访问报错
    connect_args={"check_same_thread": False},
    # 自动检测连接是否失效，避免数据库断连报错
    pool_pre_ping=True
)

# 2. 创建会话工厂，所有数据库查询都通过SessionLocal生成会话
# autocommit=False：手动提交事务，下单等操作需要手动commit保证数据安全
# autoflush=False：不自动刷新缓存，提升性能
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 项目启动自动扫描所有导入的模型，自动创建不存在的数据表
Base.metadata.create_all(bind=engine)

# 3. 依赖注入函数：每次数据库操作生成独立会话，用完自动关闭
def get_db():
    db = SessionLocal()
    try:
        # 产出数据库会话给上层service/工具使用
        yield db
    finally:
        # 无论程序是否报错，最终都会关闭会话，防止数据库连接泄漏
        db.close()