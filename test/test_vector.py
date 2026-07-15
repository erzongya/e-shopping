from vector_store.store import search_goods_vector


query = "蓝牙"
print("传入搜索文本：", query, type(query))
data = search_goods_vector(query)
print("向量检索结果：", data)

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test():
    cfg = {
        "order_mcp": {
            "url": "http://127.0.0.1:8002/mcp",
            "transport": "streamable-http",
            "headers": {
                "Authorization": "Bearer order_2026_secret",
                "Accept": "text/event-stream"
            }
        }
    }
    client = MultiServerMCPClient(cfg)
    tools = await client.get_tools()
    print("加载到工具：", [t.name for t in tools])
    # 调用查询订单工具
    for t in tools:
        if "order" in t.name.lower():
            res = await t.ainvoke({"order_id": 1})
            print("工具返回：", res)

asyncio.run(test())