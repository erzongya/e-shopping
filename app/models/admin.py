"""
管理后台数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, SmallInteger, Text
from app.models.base import BaseModel


class Admin(BaseModel):
    """管理员表"""
    __tablename__ = "admin"

    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")

    role = Column(String(50), default="operator", comment="角色: super_admin/admin/operator")
    status = Column(SmallInteger, default=1, comment="状态: 1正常 2冻结")

    last_login_time = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")


class AdminLog(BaseModel):
    """管理员操作日志表"""
    __tablename__ = "admin_log"

    admin_id = Column(String(64), nullable=False, index=True, comment="管理员ID")
    action = Column(String(100), nullable=False, comment="操作类型")
    target = Column(String(100), comment="操作对象")
    target_id = Column(String(64), comment="操作对象ID")
    content = Column(Text, comment="操作内容")
    ip = Column(String(50), comment="操作IP")
    user_agent = Column(String(500), comment="浏览器UA")