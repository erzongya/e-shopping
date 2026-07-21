# mcp_server/client/manager.py
import asyncio
from typing import List, Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from common.exception import BizErr, ErrCode
from common.logger import log_error

# 删掉token字段
MCP_SERVER_LIST = [
    {"name": "goods_mcp", "url": "http://127.0.0.1:8001/mcp", "transport": "streamable-http"},
    {"name": "order_mcp", "url": "http://127.0.0.1:8002/mcp", "transport": "streamable-http"},
    {"name": "ops_mcp", "url": "http://127.0.0.1:8003/mcp", "transport": "streamable-http"},
    {"name": "cart_mcp", "url": "http://127.0.0.1:8004/mcp", "transport": "streamable-http"},
    {"name": "user_mcp", "url": "http://127.0.0.1:8005/mcp", "transport": "streamable-http"},
    {"name": "promotion_mcp", "url": "http://127.0.0.1:8006/mcp", "transport": "streamable-http"},
    {"name": "aftersale_mcp", "url": "http://127.0.0.1:8007/mcp", "transport": "streamable-http"},
    {"name": "admin_mcp", "url": "http://127.0.0.1:8008/mcp", "transport": "streamable-http"},
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
        retry_times = 2

        for cfg in MCP_SERVER_LIST:
            svc_name = cfg["name"]
            # 移除Bearer鉴权头，只保留SSE必须请求头
            client_cfg = {
                svc_name: {
                    "url": cfg["url"],
                    "transport": cfg["transport"],
                    "headers": {
                        "Accept": "text/event-stream",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive"
                    }
                }
            }
            status = {"name": svc_name, "healthy": False, "tool_count": 0}
            tools = None

            # 重试连接逻辑保持原样
            for i in range(retry_times + 1):
                try:
                    tools = await MultiServerMCPClient(client_cfg).get_tools()
                    break
                except Exception as e:
                    err_msg = f"[MCP-CLIENT] {svc_name} 第{i + 1}次连接失败: {str(e)}"
                    print(err_msg)
                    log_error("", "system_mcp_manager", err_msg, e)
                    if i != retry_times:
                        await asyncio.sleep(1)

            if tools is not None:
                all_tools.extend(tools)
                status.update({"healthy": True, "tool_count": len(tools)})
                print(f"[MCP-CLIENT] {svc_name} 连接成功，工具数量:{len(tools)}")
            self._server_status.append(status)

        offline = self.get_offline_servers()
        if offline:
            print(f"[MCP-CLIENT] 离线服务列表: {offline}")
        print(f"[MCP-CLIENT] 全部MCP加载完成，总可用工具:{len(all_tools)}")
        return all_tools

    def get_tools(self) -> List:
        if self._tools is None:
            raise BizErr(ErrCode.MCP_CONNECT_FAIL, "MCP服务未初始化，请先执行initialize")
        return self._tools

    def get_offline_servers(self) -> List[str]:
        return [s["name"] for s in self._server_status if not s["healthy"]]

# 全局单例
mcp_manager = MCPManager()