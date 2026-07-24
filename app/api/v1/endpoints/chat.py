# app/api/v1/endpoints/chat.py
"""
聊天相关 API - 异步版
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_async_db
from app.services.chat import ChatService
from app.api.schemas.chat import ChatRequest
from app.common.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/send")
async def send_message(
        request: ChatRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    发送聊天消息（通过 Agent 处理）

    - Agent 自动调用工具处理用户请求
    - 支持多轮对话
    - 自动管理会话
    - 积分奖励
    """
    try:
        service = ChatService(db)
        result = await service.send_message(
            user_id=current_user.id,
            message=request.message,
            session_id=request.session_id,
        )

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(
        session_id: str,
        limit: int = Query(50, ge=1, le=200, description="返回数量"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取会话历史
    """
    try:
        service = ChatService(db)
        result = await service.get_history(
            user_id=current_user.id,
            session_id=session_id,
            limit=limit
        )

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions")
async def get_sessions(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户所有会话
    """
    try:
        service = ChatService(db)
        sessions = await service.get_sessions(current_user.id)

        return {
            "code": 0,
            "message": "success",
            "data": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions")
async def create_session(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    创建新会话
    """
    try:
        service = ChatService(db)
        session_id = await service.create_session(current_user.id)

        return {
            "code": 0,
            "message": "会话创建成功",
            "data": {"session_id": session_id}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
        session_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    删除会话
    """
    try:
        service = ChatService(db)
        result = await service.delete_session(current_user.id, session_id)
        if not result:
            raise HTTPException(status_code=404, detail="会话不存在")

        return {
            "code": 0,
            "message": "会话已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))