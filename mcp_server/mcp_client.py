import asyncio
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient

log = logging.getLogger("mcp-manager")

MCP_SERVER_LIST = [
    {
        "name": "goods_mcp",
        "url": "http://127.0.0.1:8001/mcp",
        "transport": "streamable-http",
        "token": "goods_2026_secret"
    },
    {
        "name": "order_mcp",
        "url": "http://127.0.0.1:8002/mcp",
        "transport": "streamable-http",
        "token": "order_2026_secret"
    },
    {
        "name": "ops_mcp",
        "url": "http://127.0.0.1:8003/mcp",
        "transport": "streamable-http",
        "token": "ops_2026_secret"
    }
]

class MCPManager:
    def __init__(self):
        self._tools = None

    async def initialize(self):
        if self._tools is None:
            self._tools = await self._async_load()
        return self._tools

    async def _async_load(self):
        if self._tools is not None:
            return self._tools
        total_tools = []
        for server in MCP_SERVER_LIST:
            cfg = {
                server["name"]: {
                    "url": server["url"],
                    "transport": server["transport"],
                    "headers": {
                        "Authorization": f"Bearer {server['token']}",
                        "Accept": "text/event-stream"
                    }
                }
            }
            client = MultiServerMCPClient(cfg)
            tools = await client.get_tools()
            total_tools.extend(tools)
            log.info(f"加载成功：{server['name']}")
            await asyncio.sleep(0.03)
        log.info(f"MCP加载完成，工具总数：{len(total_tools)}")
        self._tools = total_tools
        return self._tools

    def get_tools(self):
        if self._tools is None:
            raise RuntimeError("MCP未初始化")
        return self._tools

mcp_manager = MCPManager()