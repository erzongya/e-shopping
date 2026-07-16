from mcp.server.fastmcp import FastMCP
from mcp_server.common import batch_register_skills
from common.logger import log_error
from skill.registry import OPS_SKILL_CLS

# MCP实例仅配置业务元信息，host/port剥离到run方法
mcp = FastMCP(
    name="OpsTools",
    instructions="运维管理工具：清理过期对话会话、统计LLM Token消耗",
    log_level="ERROR",
    host="127.0.0.1",
    port = 8003
)
batch_register_skills(mcp, OPS_SKILL_CLS, log_error)
def create_server():
    """启动操作MCP服务入口"""
    print("=== 操作业务工具MCP服务器信息 ===")
    print(f"工具:功能: {mcp.name}==>{mcp.instructions}")
    try:
        print(f"服务器已启动，访问地址：http://127.0.0.1:8003/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"操作MCP服务启动失败: {e}")

if __name__ == "__main__":
    create_server()