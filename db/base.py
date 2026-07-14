# 数据库模型基类
from sqlalchemy.orm import declarative_base

# 作用：统一管理数据表元数据，执行create_all()时自动识别所有表
#ORM 映射核心，不用手写原生 SQL 建表语句；
#后续商品表、订单表继承该类，初始化脚本可一键自动创建全部数据表；

Base = declarative_base()

