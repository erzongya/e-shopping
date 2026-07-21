from mcp.server.fastmcp import FastMCP
from mcp_server.common import batch_register_skills
from common.logger import log_error
from skill.registry import GOODS_SKILL_CLS

# 企业统一配置区
SERVICE_NAME = "GoodsMCP"
SERVICE_PORT = 8001
SERVICE_HOST = "127.0.0.1"
SERVICE_DESC = "商品业务服务：商品详情查询、多条件筛选、规格查询、用户评价查询"

# 初始化MCP实例
mcp = FastMCP(
    name=SERVICE_NAME,
    instructions=SERVICE_DESC,
    log_level="ERROR",
    host=SERVICE_HOST,
    port=SERVICE_PORT,
)
# 批量注册当前域全部工具
batch_register_skills(mcp, GOODS_SKILL_CLS, log_error)

def run_server():
    """统一服务启动入口"""
    # MCP启动日志，trace_id=""，固定系统会话标识
    log_error("", "system_mcp_user", f"{SERVICE_NAME} 服务开始启动，端口{SERVICE_PORT}")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"【{SERVICE_NAME}】启动失败：{str(e)}")
        raise

if __name__ == "__main__":
    run_server()