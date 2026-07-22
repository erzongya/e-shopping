# mcp_server/client/manager.py

import asyncio
from typing import List, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from common.exception import BizErr, ErrCode
from common.logger import log_error

MCP_SERVERS = [
    {"name": "goods_mcp", "url": "http://127.0.0.1:8001/mcp"},
    {"name": "order_mcp", "url": "http://127.0.0.1:8002/mcp"},
    {"name": "ops_mcp", "url": "http://127.0.0.1:8003/mcp"},
    {"name": "cart_mcp", "url": "http://127.0.0.1:8004/mcp"},
    {"name": "user_mcp", "url": "http://127.0.0.1:8005/mcp"},
    {"name": "promotion_mcp", "url": "http://127.0.0.1:8006/mcp"},
    {"name": "aftersale_mcp", "url": "http://127.0.0.1:8007/mcp"},
    {"name": "admin_mcp", "url": "http://127.0.0.1:8008/mcp"},
]


class MCPManager:
    def __init__(self):
        self._tools: Optional[List] = None
        self._tools_meta: Dict = {}
        self._offline_servers: List[str] = []

    async def initialize(self) -> List:
        """加载所有MCP工具"""
        if self._tools is not None:
            return self._tools

        self._tools = []
        self._tools_meta = {}
        self._offline_servers = []

        for server in MCP_SERVERS:
            tools = await self._connect_server(server)
            if tools:
                self._tools.extend(tools)
                self._cache_tools_meta(tools)
            else:
                self._offline_servers.append(server["name"])

        print(f"[MCP] 加载完成: {len(self._tools)} 个工具, 离线服务: {self._offline_servers}")
        return self._tools

    async def _connect_server(self, server: dict) -> Optional[List]:
        """连接单个MCP服务"""
        name, url = server["name"], server["url"]
        config = {
            name: {
                "url": url,
                "transport": "streamable-http",
                "headers": {"Accept": "text/event-stream", "Cache-Control": "no-cache"}
            }
        }

        for attempt in range(3):
            try:
                tools = await MultiServerMCPClient(config).get_tools()
                print(f"[MCP] ✅ {name} 连接成功, {len(tools)} 个工具")
                return tools
            except Exception as e:
                print(f"[MCP] ⚠️ {name} 第{attempt + 1}次连接失败")
                log_error("", "mcp_manager", f"{name}连接失败", e)
                if attempt < 2:
                    await asyncio.sleep(1)

        print(f"[MCP] ❌ {name} 连接失败")
        return None

    def _cache_tools_meta(self, tools: List):
        """缓存工具元数据"""
        for tool in tools:
            # 获取 schema（MCP Adapter 返回的已经是字典）
            schema = {}
            if hasattr(tool, "args_schema") and isinstance(tool.args_schema, dict):
                schema = tool.args_schema
            if schema.get("properties", {}).keys() == {"kwargs"}:
                schema = {
                    "type": "object",
                    "properties": {
                        "params": {
                            "type": "object",
                            "description": "业务参数（JSON对象）"
                        }
                    },
                    "required": ["params"]
                }
            # 如果 schema 为空，用默认值
            if not schema:
                schema = {"type": "object", "properties": {}}

            self._tools_meta[tool.name] = {
                "description": tool.description or f"{tool.name}工具",
                "schema": schema
            }

    def get_tools(self) -> List:
        if self._tools is None:
            raise BizErr(ErrCode.MCP_CONNECT_FAIL, "MCP未初始化")
        return self._tools

    def get_tools_meta(self) -> Dict:
        return self._tools_meta

    def get_offline_servers(self) -> List[str]:
        return self._offline_servers


mcp_manager = MCPManager()