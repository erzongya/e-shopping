# 用户会员域
from sqlalchemy import Column, String, Integer, Numeric, DateTime, SmallInteger
from db.base import Base

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(String(64), primary_key=True, comment="用户唯一ID")
    nickname = Column(String(100), comment="用户昵称")
    phone = Column(String(20), comment="手机号")
    vip_level = Column(SmallInteger, default=1, comment="会员等级1~5")
    point = Column(Integer, default=0, comment="可用积分")
    register_time = Column(DateTime, comment="注册时间")


class UserAddress(Base):
    __tablename__ = "user_address"
    id = Column(String(64), primary_key=True, comment="地址ID")
    user_id = Column(String(64), nullable=False, comment="所属用户ID")
    name = Column(String(50), nullable=False, comment="收件人姓名")
    phone = Column(String(20), nullable=False, comment="收件手机号")
    address = Column(String(500), nullable=False, comment="完整收货地址")


class UserSignIn(Base):
    __tablename__ = "user_sign_in"
    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    sign_date = Column(String(32), comment="签到日期 yyyy-MM-dd")
    reward_point = Column(Integer, default=10, comment="当日签到积分")
    create_time = Column(DateTime)