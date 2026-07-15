from skill.goods.vector_search import SearchSimilarGoodsSkill
from skill.goods.detail_query import GetGoodsDetailSkill
from skill.goods.filter import FilterGoodsSkill

from skill.order.query_order import QueryOrderSkill
from skill.order.return_check import CheckReturnEligibilitySkill

from skill.ops.clean_expire_checkpoint import CleanExpireCheckpointSkill
from skill.base import BaseSkill
from langchain_core.tools import StructuredTool


# ========== 1. 按业务域拆分技能分组（适配分域MCP） ==========
GOODS_SKILL_LIST = [
    SearchSimilarGoodsSkill(),
    GetGoodsDetailSkill(),
    FilterGoodsSkill()
]

ORDER_SKILL_LIST = [
    QueryOrderSkill(),
    CheckReturnEligibilitySkill()
]

OPS_SKILL_LIST = [
    CleanExpireCheckpointSkill()
]

# 全局合并注册表（本地开发全量加载）
SKILL_REGISTRY = {}
# 合并商品技能
for sk in GOODS_SKILL_LIST:
    SKILL_REGISTRY[sk.name] = sk
# 合并订单技能
for sk in ORDER_SKILL_LIST:
    SKILL_REGISTRY[sk.name] = sk
# 合并运维技能
for sk in OPS_SKILL_LIST:
    SKILL_REGISTRY[sk.name] = sk


# ========== 2. 你原有工具转换方法完全保留 ==========
def skill_to_tool(skill: BaseSkill) -> StructuredTool:
    return StructuredTool.from_function(
        func=skill.run,
        name=skill.name,
        description=skill.description,
        args_schema=skill.params_model  # 直接传入Pydantic模型，自动生成参数说明
    )


# ========== 3. 分域获取工具函数（给各独立MCP服务调用） ==========
def get_goods_skills() -> list[StructuredTool]:
    """商品MCP专用：仅返回商品类工具"""
    return [skill_to_tool(sk) for sk in GOODS_SKILL_LIST]

def get_order_skills() -> list[StructuredTool]:
    """订单MCP专用：仅返回订单类工具"""
    return [skill_to_tool(sk) for sk in ORDER_SKILL_LIST]

def get_ops_skills() -> list[StructuredTool]:
    """运维MCP专用：仅返回运维清理工具"""
    return [skill_to_tool(sk) for sk in OPS_SKILL_LIST]

# ========== 4. 原有全量获取函数兼容不动（本地开发用） ==========
def get_all_skills() -> list[StructuredTool]:
    """本地单Agent开发，加载全部业务工具"""
    return [skill_to_tool(sk) for sk in SKILL_REGISTRY.values()]