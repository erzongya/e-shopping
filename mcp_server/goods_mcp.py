from mcp.server.fastmcp import FastMCP
import os
from skill.registry import GOODS_SKILL_LIST
import uvicorn
# 鉴权密钥从环境变量读取
MCP_GOODS_TOKEN = os.getenv("MCP_GOODS_TOKEN", "goods_2026_secret")

# 仅填写业务元信息，不写网络端口
goods_mcp = FastMCP(
    name="GoodsTools",
    instructions="商品业务工具：语义向量检索商品、查询商品详情、按价格库存过滤商品",
    log_level="ERROR",
    host="127.0.0.1",
    port=8001
)

# 批量注册商品域Skill，统一调用execute封装通用逻辑
for skill in GOODS_SKILL_LIST:
    def wrap_skill(sk):
        @goods_mcp.tool(name=sk.name, description=sk.description)
        def run_func(**kwargs):
            return sk.execute(**kwargs)

def create_server():
    # 打印服务器信息
    print("=== 商品业务工具MCP服务器信息 ===")
    print(f"名称: {goods_mcp.name}")
    print(f"描述: {goods_mcp.instructions}")

    # 运行服务器
    try:
        print("服务器已启动，请访问 http://127.0.0.1:8001/mcp")
        goods_mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"服务器启动失败: {e}")

if __name__ == "__main__":
    create_server()