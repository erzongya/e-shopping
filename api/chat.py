from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from agent.context import get_agent_graph
from common.logger import log_info
import asyncio
# 路由实例（用于main挂载）
router = APIRouter()

# 请求体模型
class ChatBody(BaseModel):
    question: str

# 全局提前构建graph


# 对话接口
@router.post("/chat")
async def chat_api(
    req_data: ChatBody,
    request: Request,
    X_Session_Id: str = Header(..., alias="X-Session-Id")
):
    trace_id = getattr(request.state, "trace_id", "")
    log_info(trace_id, X_Session_Id, f"用户提问：{req_data.question}")

    graph = get_agent_graph()
    input_state = {
        "messages": [HumanMessage(content=req_data.question)],
        "tool_records": [],  # 初始化为空
        "error_info": None,
        "user_id": None,  # 可以从请求中获取用户ID
        "tool_call_round": 0
    }
    cfg = {"configurable": {"thread_id": X_Session_Id, "checkpoint_ns": "e_shop"}}
    res = await graph.ainvoke(input_state, config=cfg)
    answer = res["messages"][-1].content
    return {
        "code": 200,
        "msg": "ok",
        "data": {"answer": answer}
    }