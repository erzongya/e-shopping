# app/services/chat.py
"""
聊天业务逻辑服务 - 异步版
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime
import uuid

from app.models.chat import ChatHistory, ChatSession
from app.models.user import User
from app.agent.manager import agent_manager
from app.core.logger import log_info, log_error
from langchain_core.messages import HumanMessage, AIMessage


class ChatService:
    """聊天业务服务 - 异步"""

    def __init__(self, db: AsyncSession):
        """初始化聊天服务，注入数据库会话"""
        self.db = db

    # ==================== 会话管理 ====================

    async def create_session(self, user_id: str, title: str = "新对话") -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID
            title: 会话标题（默认"新对话"）

        Returns:
            session_id: 新创建的会话ID
        """
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(session)
        await self.db.commit()
        return session_id

    async def save_message(self, user_id: str, session_id: str, role: str, content: str):
        """
        保存单条消息到数据库

        Args:
            user_id: 用户ID
            session_id: 会话ID
            role: 消息角色 (user/assistant/system)
            content: 消息内容
        """
        msg = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.now()
        )
        self.db.add(msg)
        await self.db.commit()

    async def get_history(self, user_id: str, session_id: str, limit: int = 10) -> List[Dict]:
        """
        获取会话历史消息（最近N条）

        Args:
            user_id: 用户ID
            session_id: 会话ID
            limit: 返回条数（默认10条）

        Returns:
            消息列表: [{"role": "user", "content": "你好"}, ...]
        """
        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id, ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at)
            .limit(limit)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages]

    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户所有会话列表

        Args:
            user_id: 用户ID

        Returns:
            会话列表: [{"session_id": "...", "title": "...", "message_count": 5, "last_update": ...}]
        """
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.is_deleted == False)
            .order_by(desc(ChatSession.updated_at))
        )
        sessions = result.scalars().all()

        result_list = []
        for session in sessions:
            # 统计每个会话的消息数量
            count_result = await self.db.execute(
                select(func.count(ChatHistory.id)).where(ChatHistory.session_id == session.id)
            )
            msg_count = count_result.scalar()
            result_list.append({
                "session_id": session.id,
                "title": session.title,
                "message_count": msg_count,
                "last_update": session.updated_at
            })
        return result_list

    async def delete_session(self, user_id: str, session_id: str) -> bool:
        """
        软删除会话（标记 is_deleted=True）

        Args:
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return False
        session.is_deleted = True
        await self.db.commit()
        return True

    # ==================== 核心聊天 ====================

    async def send_message(
            self,
            user_id: str,
            message: str,
            session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送消息并获取 AI 回复（核心方法）

        流程：
        1. 获取/创建会话
        2. 保存用户消息
        3. 获取历史消息
        4. 转换为 LangChain 格式
        5. 调用 Agent Graph
        6. 提取 AI 回复
        7. 保存 AI 回复
        8. 返回结果

        Args:
            user_id: 用户ID
            message: 用户输入的消息
            session_id: 会话ID（可选，不传则创建新会话）

        Returns:
            {"session_id": "...", "message": "AI回复内容"}
        """

        # 1. 获取或创建会话
        if not session_id:
            session_id = await self.create_session(user_id)

        # 2. 保存用户消息到数据库
        await self.save_message(user_id, session_id, "user", message)

        # 3. 检查 Agent 是否就绪
        if not agent_manager.is_ready():
            log_error("", session_id, "Agent 未就绪")
            ai_response = "服务正在初始化，请稍后再试。"
        else:
            try:
                # 4. 获取编译好的 Agent Graph
                graph = agent_manager.get_graph()

                # 5. 获取历史消息（用于上下文）
                history = await self.get_history(user_id, session_id)

                # 6. 转换为 LangChain 消息格式
                lc_messages = []
                for msg in history:
                    if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        lc_messages.append(AIMessage(content=msg["content"]))
                # 添加当前用户消息
                lc_messages.append(HumanMessage(content=message))

                # 7. 构建 Agent 输入状态
                input_state = {
                    "messages": lc_messages,  # 对话历史
                    "call_count": 0,  # 工具调用次数
                    "user_id": user_id,  # 用户标识
                    "session_id": session_id,  # 会话标识
                    "current_query": message  # 当前问题
                }

                # 8. 配置（用于状态持久化）
                config = {
                    "configurable": {
                        "thread_id": session_id,  # 用 session_id 做 thread_id
                        "user_id": user_id
                    }
                }

                # 9. 调用 Agent（异步执行）
                log_info("", session_id, f"Agent 开始处理: {message[:50]}...")
                result = await graph.ainvoke(input_state, config=config)

                # 10. 提取 AI 回复
                ai_messages = result.get("messages", [])
                if ai_messages:
                    last_msg = ai_messages[-1]
                    ai_response = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                else:
                    ai_response = "抱歉，我无法处理您的请求。"

                log_info("", session_id, "Agent 回复成功")

            except Exception as e:
                log_error("", session_id, "Agent 执行失败", e)
                ai_response = "服务暂时不可用，请稍后再试。"

        # 11. 保存 AI 回复到数据库
        await self.save_message(user_id, session_id, "assistant", str(ai_response))

        # 12. 返回结果
        return {
            "session_id": session_id,
            "message": str(ai_response)
        }