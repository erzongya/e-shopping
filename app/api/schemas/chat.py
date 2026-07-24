# app/api/schemas/chat.py
"""
聊天相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，不传则创建新会话")
    model: str = Field("gpt-3.5-turbo", description="使用的模型")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    message: str
    tokens_used: int
    remaining_tokens: int
    model: str


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    session_id: str
    messages: List[dict]
    total: int


class ChatSessionResponse(BaseModel):
    """聊天会话响应"""
    session_id: str
    title: str
    message_count: int
    last_update: datetime