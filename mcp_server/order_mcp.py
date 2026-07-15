from mcp.server.fastmcp import FastMCP
import os
from skill.registry import ORDER_SKILL_LIST
import uvicorn
MCP_ORDER_TOKEN = os.getenv("MCP_ORDER_TOKEN", "order_2026_secret")

order_mcp = FastMCP(
    name="OrderTools",
    instructions="订单售后工具：查询用户历史订单、校验商品退货资格",
    log_level="ERROR",
    host="127.0.0.1",
    port=8002
)

for skill in ORDER_SKILL_LIST:
    def wrap_skill(sk):
        @order_mcp.tool(name=sk.name, description=sk.description)
        def run_func(**kwargs):
            return sk.execute(**kwargs)



def create_server():
    # 打印服务器信息
    print("=== 订单售后MCP服务器信息 ===")
    print(f"名称: {order_mcp.name}")
    print(f"描述: {order_mcp.instructions}")

    # 运行服务器
    try:
        print("服务器已启动，请访问 http://127.0.0.1:8002/mcp")
        order_mcp.run(transport="streamable-http")  # 使用 streamable-http 传输方式
    except Exception as e:
        print(f"服务器启动失败: {e}")
if __name__ == "__main__":
    create_server()