"""
聊天数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from app.models.base import BaseModel


class ChatSession(BaseModel):
    """聊天会话表"""
    __tablename__ = "chat_sessions"

    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    title = Column(String(200), default="新对话", comment="会话标题")
    created_at = Column(DateTime, comment="创建时间")
    updated_at = Column(DateTime, comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")


class ChatHistory(BaseModel):
    """聊天历史表"""
    __tablename__ = "chat_history"

    user_id = Column(String(64), nullable=False, index=True, comment="用户ID")
    session_id = Column(String(64), nullable=False, index=True, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    tokens_used = Column(Integer, default=0, comment="使用的token数")
    model = Column(String(50), comment="使用的模型")
    created_at = Column(DateTime, comment="创建时间")