"""
购物车 MCP 服务
"""
from mcp.server.fastmcp import FastMCP
from app.mcp_server.services.common import batch_register_skills
from app.core.logger import log_info,log_error
from app.mcp_server.skills.cart import CART_SKILL_CLS

SERVICE_NAME = "CartMCP"
SERVICE_PORT = 8004
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "购物车工具服务：添加购物车、更新数量、移除商品、切换选中状态、获取购物车列表"

mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
batch_register_skills(mcp, CART_SKILL_CLS, log_error)


def run_server():
    log_info("", "system_mcp_cart", f"{SERVICE_NAME} 服务启动，端口 {SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise


if __name__ == "__main__":
    run_server()