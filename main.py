from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent.graph import graph
import uvicorn
app = FastAPI(title='电商客服Agent接口')

# 请求体结构
class ChatReq(BaseModel):
    session_id:str
    question:str

# 内存简易会话存储
session_cache = {}

@app.get("/")
def index():
    return {"msg": "电商客服API服务运行中，请访问 /docs 调试接口"}
@app.post('/chat')
def chat(req:ChatReq):
    # 读取/初始化会话记忆
    if req.session_id not in session_cache:
        session_cache[req.session_id] = {
            "messages": [],
            "goods_ids": [],
            "goods_info": []
        }
    state = session_cache[req.session_id]
    #追加 用户提问
    state["messages"].append(HumanMessage(content=req.question))
    # 执行 agent流程
    state = graph.invoke(state)
    # 保存更新后的会话
    session_cache[req.session_id] = state
    # 返回客服回复
    reply = state['messages'][-1].content
    return {"answer": reply}

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8001,reload=True)

