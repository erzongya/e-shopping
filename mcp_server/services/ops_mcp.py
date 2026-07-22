from mcp.server.fastmcp import FastMCP
from mcp_server.services.common import batch_register_skills
from common.logger import log_error
from mcp_server.skill import OPS_SKILL_CLS

SERVICE_NAME = "OpsMCP"
SERVICE_PORT = 8003
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "仓储库存服务：校验商品库存是否充足、运营后台修改商品库存数量"

mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
batch_register_skills(mcp, OPS_SKILL_CLS, log_error)

def run_server():
    # MCP启动日志，trace_id=""，固定系统会话标识
    log_error("", "system_mcp_user", f"{SERVICE_NAME} 服务开始启动，端口{SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise

if __name__ == "__main__":
    run_server()