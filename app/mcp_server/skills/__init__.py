# """
# MCP 技能注册中心
# """
# from app.mcp_server.skills.base import BaseSkill, SkillParams
#
# from app.mcp_server.skills.goods import GOODS_SKILL_CLS
# from app.mcp_server.skills.user import USER_SKILL_CLS
# from app.mcp_server.skills.order import ORDER_SKILL_CLS
# from app.mcp_server.skills.cart import CART_SKILL_CLS
# from app.mcp_server.skills.promotion import PROMOTION_SKILL_CLS
# from app.mcp_server.skills.aftersale import AFTERSALE_SKILL_CLS
# from app.mcp_server.skills.admin import ADMIN_SKILL_CLS
# from app.mcp_server.skills.ops import OPS_SKILL_CLS
#
# __all__ = [
#     "BaseSkill",
#     "SkillParams",
#     "GOODS_SKILL_CLS",
#     "USER_SKILL_CLS",
#     "ORDER_SKILL_CLS",
#     "CART_SKILL_CLS",
#     "PROMOTION_SKILL_CLS",
#     "AFTERSALE_SKILL_CLS",
#     "ADMIN_SKILL_CLS",
#     "OPS_SKILL_CLS",
# ]
#
# # 所有技能汇总
# ALL_SKILL_CLS = (
#     GOODS_SKILL_CLS +
#     USER_SKILL_CLS +
#     ORDER_SKILL_CLS +
#     CART_SKILL_CLS +
#     PROMOTION_SKILL_CLS +
#     AFTERSALE_SKILL_CLS +
#     ADMIN_SKILL_CLS +
#     OPS_SKILL_CLS
# )