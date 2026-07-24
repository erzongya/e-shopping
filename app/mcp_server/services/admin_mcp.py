"""
管理员 MCP 服务
"""
from mcp.server.fastmcp import FastMCP
from app.mcp_server.services.common import batch_register_skills
from app.core.logger import log_error,log_info
from app.mcp_server.skills.admin import ADMIN_SKILL_CLS

SERVICE_NAME = "AdminMCP"
SERVICE_PORT = 8008
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "管理后台工具服务：管理员登录、创建管理员、管理员列表、操作日志查询"

mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
batch_register_skills(mcp, ADMIN_SKILL_CLS, log_error)


def run_server():
    log_info("", "system_mcp_admin", f"{SERVICE_NAME} 服务启动，端口 {SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise


if __name__ == "__main__":
    run_server()