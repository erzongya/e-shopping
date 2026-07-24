"""
订单 MCP 服务
"""
from mcp.server.fastmcp import FastMCP
from app.mcp_server.services.common import batch_register_skills
from app.core.logger import log_info,log_error
from app.mcp_server.skills.order import ORDER_SKILL_CLS

SERVICE_NAME = "OrderMCP"
SERVICE_PORT = 8002
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "订单物流服务：按用户/状态查询订单、根据快递单号查询完整物流轨迹"

mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
batch_register_skills(mcp, ORDER_SKILL_CLS, log_error)


def run_server():
    log_info("", "system_mcp_order", f"{SERVICE_NAME} 服务启动，端口 {SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise


if __name__ == "__main__":
    run_server()