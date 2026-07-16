from skill.goods.vector_search import SearchSimilarGoodsSkill
from skill.goods.detail_query import GetGoodsDetailSkill
from skill.goods.filter import FilterGoodsSkill
from skill.order.query_order import QueryOrderSkill
from skill.order.return_check import CheckReturnEligibilitySkill
from skill.ops.clean_expire_checkpoint import CleanExpireCheckpointSkill
from skill.base import BaseSkill
from langchain_core.tools import StructuredTool
from typing import Type, List


# 1. 分领域技能类定义
GOODS_SKILL_CLS: List[Type[BaseSkill]] = [
    SearchSimilarGoodsSkill,
    GetGoodsDetailSkill,
    FilterGoodsSkill
]
ORDER_SKILL_CLS: List[Type[BaseSkill]] = [
    QueryOrderSkill,
    CheckReturnEligibilitySkill
]
OPS_SKILL_CLS: List[Type[BaseSkill]] = [
    CleanExpireCheckpointSkill
]


# 2. 公共工具转换函数
def skill_to_tool(skill: BaseSkill) -> StructuredTool:
    return StructuredTool.from_function(
        func=skill.run,
        name=skill.name,
        description=skill.description,
        args_schema=skill.params_model
    )


# 3. 公共批量转换封装（消除重复循环）
def batch_convert(skill_classes: List[Type[BaseSkill]]) -> List[StructuredTool]:
    skill_instances = [cls() for cls in skill_classes]
    return [skill_to_tool(sk) for sk in skill_instances]


# 4. 分域导出，给对应mcp文件调用
def get_goods_skills() -> List[StructuredTool]:
    return batch_convert(GOODS_SKILL_CLS)

def get_order_skills() -> List[StructuredTool]:
    return batch_convert(ORDER_SKILL_CLS)

def get_ops_skills() -> List[StructuredTool]:
    return batch_convert(OPS_SKILL_CLS)


# 5. 本地调试全量加载
def get_all_skills() -> List[StructuredTool]:
    all_cls = GOODS_SKILL_CLS + ORDER_SKILL_CLS + OPS_SKILL_CLS
    return batch_convert(all_cls)