# mcp_server/client/mcp_manager.py

import asyncio
from typing import List, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.common.exceptions import BusinessException
from app.core.logger import log_error

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

        # ✅ 只打印一行，不打印离线服务（除非有离线）
        if self._offline_servers:
            print(f"[MCP] 加载完成: {len(self._tools)} 个工具, 离线: {self._offline_servers}")
        else:
            print(f"[MCP] 加载完成: {len(self._tools)} 个工具")
        return self._tools

    async def _connect_server(self, server: dict) -> Optional[List]:
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
                # ✅ 只打印成功，不打印工具数量
                print(f"[MCP] ✅ {name} 已连接")
                return tools
            except Exception as e:
                # ✅ 只在最后失败时打印，不打印每次重试
                if attempt == 2:
                    print(f"[MCP] ❌ {name} 连接失败")
                    log_error("", "mcp_manager", f"{name}连接失败", e)
                if attempt < 2:
                    await asyncio.sleep(1)

        return None

    def _cache_tools_meta(self, tools: List):
        """缓存工具元数据"""
        for tool in tools:
            schema = {}

            if hasattr(tool, "args_schema"):
                args_schema = tool.args_schema

                if hasattr(args_schema, "model_json_schema"):
                    schema = args_schema.model_json_schema()
                elif hasattr(args_schema, "schema"):
                    schema = args_schema.schema()
                elif isinstance(args_schema, dict):
                    schema = args_schema

            # ✅ 展开 params
            properties = schema.get("properties", {})
            if "params" in properties:
                params_schema = properties["params"]

                # 处理 $ref
                if "$ref" in params_schema:
                    ref_name = params_schema["$ref"].replace("#/$defs/", "")
                    params_schema = schema.get("$defs", {}).get(ref_name, {})

                # 展开嵌套
                if isinstance(params_schema, dict) and params_schema.get("type") == "object":
                    nested = params_schema.get("properties", {})
                    if nested:
                        schema["properties"] = nested
                        schema["required"] = params_schema.get("required", [])
                        # 删除 $defs 保持干净
                        schema.pop("$defs", None)

            if not schema:
                schema = {"type": "object", "properties": {}}

            self._tools_meta[tool.name] = {
                "description": tool.description or f"{tool.name}工具",
                "schema": schema
            }

    def get_tools(self) -> List:
        if self._tools is None:
            raise BusinessException( "MCP未初始化")
        return self._tools

    def get_tools_meta(self) -> Dict:
        return self._tools_meta

    def get_offline_servers(self) -> List[str]:
        return self._offline_servers


mcp_manager = MCPManager()