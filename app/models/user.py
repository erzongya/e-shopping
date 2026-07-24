"""
用户模块数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, SmallInteger, Boolean, Numeric, Text
from datetime import datetime
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    nickname = Column(String(100), nullable=False, comment="用户昵称")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    avatar = Column(String(500), comment="头像URL")
    email = Column(String(100), comment="邮箱")

    vip_level = Column(SmallInteger, default=1, comment="会员等级1-5")
    vip_expire_time = Column(DateTime, comment="会员到期时间")
    point = Column(Integer, default=0, comment="可用积分")
    total_spent = Column(Numeric(10, 2), default=0.00, comment="累计消费")

    status = Column(SmallInteger, default=1, comment="状态1正常2冻结3删除")
    last_login_time = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    register_time = Column(DateTime, default=datetime.now, comment="注册时间")


class UserAddress(BaseModel):
    __tablename__ = "user_address"

    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="收货人姓名")
    phone = Column(String(20), nullable=False, comment="收货人手机")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    address = Column(String(500), nullable=False, comment="详细地址")
    is_default = Column(Boolean, default=False, comment="是否默认地址")