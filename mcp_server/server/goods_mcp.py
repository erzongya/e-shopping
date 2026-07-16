from mcp.server.fastmcp import FastMCP
from mcp_server.common import batch_register_skills
from common.logger import log_error
from skill.registry import GOODS_SKILL_CLS

# MCP实例仅配置业务元信息，host/port剥离到run方法
mcp = FastMCP(
    name="GoodsTools",
    instructions="商品业务工具：语义向量检索商品、查询商品详情、按价格库存过滤商品",
    log_level="ERROR",
    host="127.0.0.1",
    port = 8001
)
batch_register_skills(mcp, GOODS_SKILL_CLS, log_error)
def create_server():
    """启动商品MCP服务入口"""
    print("=== 商品业务工具MCP服务器信息 ===")
    print(f"工具:功能: {mcp.name}==>{mcp.instructions}")
    try:
        print(f"服务器已启动，访问地址：http://127.0.0.1:8001/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        log_error(msg=f"商品MCP服务启动失败: {e}")

if __name__ == "__main__":
    create_server()