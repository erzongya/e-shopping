# mcp_server/client/manager.py
import asyncio
from typing import List, Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from common.exception import BizErr, ErrCode
from common.logger import log_error

# MCP集群配置（与各域MCP端口token一一对应）
MCP_SERVER_LIST = [
    {"name": "goods_mcp", "url": "http://127.0.0.1:8001/mcp", "transport": "streamable-http", "token": "goods_2026_secret"},
    {"name": "order_mcp", "url": "http://127.0.0.1:8002/mcp", "transport": "streamable-http", "token": "order_2026_secret"},
    {"name": "ops_mcp", "url": "http://127.0.0.1:8003/mcp", "transport": "streamable-http", "token": "ops_2026_secret"},
]

class MCPManager:
    def __init__(self):
        self._tools: List | None = None
        self._server_status: List[Dict] = []

    async def initialize(self) -> List:
        if self._tools is not None:
            return self._tools
        self._tools = await self._load_all()
        return self._tools

    async def _load_all(self) -> List:
        all_tools = []
        self._server_status.clear()

        for cfg in MCP_SERVER_LIST:
            svc_name = cfg["name"]
            # 抽离统一构造配置，消除重复字典代码
            client_cfg = {
                svc_name: {
                    "url": cfg["url"],
                    "transport": cfg["transport"],
                    "headers": {"Authorization": f"Bearer {cfg['token']}", "Accept": "text/event-stream"}
                }
            }
            status = {"name": svc_name, "healthy": False, "tool_count": 0}
            try:
                tools = await MultiServerMCPClient(client_cfg).get_tools()
                all_tools.extend(tools)
                status.update({"healthy": True, "tool_count": len(tools)})
                print(f"[MCP] {svc_name} 连接成功，工具数量:{len(tools)}")
            except Exception as e:
                print(f"[MCP] {svc_name} 连接失败: {str(e)}")
            self._server_status.append(status)

        offline = self.get_offline_servers()
        if offline:
            print(f"[MCP] 离线服务: {offline}")
        print(f"[MCP] 加载完成，总可用工具:{len(all_tools)}")
        return all_tools

    def get_tools(self) -> List:
        if self._tools is None:
            raise BizErr(ErrCode.MCP_CONNECT_FAIL, "MCP服务未初始化，请先执行initialize")
        return self._tools

    def get_offline_servers(self) -> List[str]:
        return [s["name"] for s in self._server_status if not s["healthy"]]


# 全局单例
mcp_manager = MCPManager()