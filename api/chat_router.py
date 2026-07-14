from fastapi import APIRouter, Header, Request
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent.graph import graph
from common.exception import BizErr, ErrCode
from common.logger import log_info
from agent.state import AgentState

# 创建路由实例
router = APIRouter(prefix="/chat", tags=["对话接口"])

# 请求体模型
class ChatRequest(BaseModel):
    question: str

@router.post("")
async def chat(
    request: Request,
    req: ChatRequest,
    X_Session_Id: str = Header(..., alias="X-Session-Id")
):
    trace_id = getattr(request.state, "trace_id", "")
    # 参数校验
    if not X_Session_Id:
        raise BizErr(ErrCode.PARAM, "请求头 X-Session-Id 不能为空")
    if not req.question.strip():
        raise BizErr(ErrCode.PARAM, "提问内容不能为空")

    log_info(trace_id, X_Session_Id, f"用户提问：{req.question}")

    config = {"configurable": {"thread_id": X_Session_Id}}

    input_state: AgentState = {
        "messages": [HumanMessage(content=req.question)],
        "goods_ids": [],
        "goods_info": []
    }
    resp = graph.invoke(input_state, config=config)

    log_info(trace_id, X_Session_Id, "AI回复完成")
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "answer": resp['messages'][-1].content,
            "session_id": X_Session_Id
        },
        "trace_id": trace_id
    }