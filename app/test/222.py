import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_mcp():
    config = {
        "goods_mcp": {
            "url": "http://127.0.0.1:8001/mcp",
            "transport": "streamable-http",
            "headers": {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
        }
    }

    client = MultiServerMCPClient(config)
    tools = await client.get_tools()

    # 调用 list_goods_by_filter，用 kwargs 包装
    for tool in tools:
        if tool.name == "list_goods_by_filter":
            print("\n调用 list_goods_by_filter...")
            # ✅ 用 kwargs 包装参数
            result = await tool.ainvoke({"kwargs": '{"keyword": "书"}'})
            print(f"结果: {result}")
            break


asyncio.run(test_mcp())