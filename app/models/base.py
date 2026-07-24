"""
数据库模型基类
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String
from datetime import datetime
import uuid

Base = declarative_base()


class BaseModel(Base):
    """基础模型，包含通用字段"""
    __abstract__ = True

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")