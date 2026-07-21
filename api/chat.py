from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# 导入图构建方法
from agent.graph import create_agent_graph
# 导入全局初始化好的工具列表（你自己项目实际导入）
from mcp_server.client.manager import mcp_manager
from common.exception import BizErr
from common.logger import log_info

# 路由实例（用于main挂载）
router = APIRouter()

# 请求体模型
class ChatBody(BaseModel):
    question: str

# 全局提前构建graph
async def get_graph():
    tools = await mcp_manager.initialize()
    return create_agent_graph(tools)

# 对话接口
@router.post("/chat")
async def chat_api(
    req_data: ChatBody,
    request: Request,
    X_Session_Id: str = Header(..., alias="X-Session-Id")
):
    trace_id = getattr(request.state, "trace_id", "")
    log_info(trace_id, X_Session_Id, f"用户提问：{req_data.question}")

    graph = await get_graph()
    input_state = {
        "messages": [HumanMessage(content=req_data.question)],
        "goods_ids": [],
        "goods_info": []
    }
    cfg = {"configurable": {"thread_id": X_Session_Id}}
    res = await graph.ainvoke(input_state, config=cfg)
    answer = res["messages"][-1].content
    return {
        "code": 200,
        "msg": "ok",
        "data": {"answer": answer}
    }