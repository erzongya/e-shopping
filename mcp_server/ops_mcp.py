from mcp.server.fastmcp import FastMCP
import os
from skill.registry import OPS_SKILL_LIST

import uvicorn
MCP_OPS_TOKEN = os.getenv("MCP_OPS_TOKEN", "ops_2026_secret")

ops_mcp = FastMCP(
    name="OpsTools",
    instructions="运维管理工具：清理过期对话会话、统计LLM Token消耗",
    log_level="ERROR",
    host="0.0.0.0",
    port=8003
)

for skill in OPS_SKILL_LIST:
    def wrap_skill(sk):
        @ops_mcp.tool(name=sk.name, description=sk.description)
        def run_func(**kwargs):
            return sk.execute(**kwargs)


def create_server():
    # 打印服务器信息
    print("=== 运维管理工具MCP服务器信息 ===")
    print(f"名称: {ops_mcp.name}")
    print(f"描述: {ops_mcp.instructions}")

    # 运行服务器
    try:
        print("服务器已启动，请访问 http://127.0.0.1:8003/mcp")
        ops_mcp.run(transport="streamable-http")  # 使用 streamable-http 传输方式
    except Exception as e:
        print(f"服务器启动失败: {e}")
if __name__ == "__main__":
    create_server()
