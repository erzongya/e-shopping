from mcp.server.fastmcp import FastMCP
from mcp_server.common import batch_register_skills
from common.logger import logger,log_error
from skill.registry import ORDER_SKILL_CLS

# MCP实例仅配置业务元信息，host/port剥离到run方法
mcp = FastMCP(
    name="OrderTools",
    instructions="订单售后工具：查询用户历史订单、校验商品退货资格",
    log_level="ERROR",
    host="127.0.0.1",
    port = 8002
)
batch_register_skills(mcp, ORDER_SKILL_CLS, logger)
def create_server():
    """启动订单MCP服务入口"""
    print("=== 订单业务工具MCP服务器信息 ===")
    print(f"工具:功能: {mcp.name}==>{mcp.instructions}")
    try:
        print(f"服务器已启动，访问地址：http://127.0.0.1:8002/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"订单MCP服务启动失败: {e}")

if __name__ == "__main__":
    create_server()