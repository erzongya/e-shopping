"""
商品 MCP 服务
"""
from mcp.server.fastmcp import FastMCP
from app.mcp_server.services.common import batch_register_skills
from app.core.logger import log_info,log_error
from app.mcp_server.skills.goods import GOODS_SKILL_CLS
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SERVICE_NAME = "GoodsMCP"
SERVICE_PORT = 8001
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "商品工具服务：查询商品详情、商品列表筛选、秒杀商品、商品评论、商品分类"

mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
batch_register_skills(mcp, GOODS_SKILL_CLS, log_error)


def run_server():
    log_info("", "system_mcp_goods", f"{SERVICE_NAME} 启动，端口 {SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise


if __name__ == "__main__":
    run_server()