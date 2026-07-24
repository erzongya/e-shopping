# app/mcp_server/skills/user.py
"""
用户 MCP 技能 - 异步版
"""
from typing import Dict, Any
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.user import AsyncUserService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数 ==========

class GetUserProfileParams(SkillParams):
    """获取用户信息参数"""
    user_id: str = Field(description="用户ID")


class UpdateNicknameParams(SkillParams):
    """更新昵称参数"""
    user_id: str = Field(description="用户ID")
    nickname: str = Field(description="新昵称")


class GetUserAddressesParams(SkillParams):
    """获取用户地址参数"""
    user_id: str = Field(description="用户ID")


# ========== 技能 ==========

class GetUserProfileSkill(BaseSkill):
    """获取用户信息"""
    name = "get_user_profile"
    description = "获取用户基本信息"
    params_model = GetUserProfileParams

    # ✅ 改为纯异步，删除同步 run 和 _run_async
    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncUserService(db)
                data = await service.get_profile(args.user_id)
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class UpdateNicknameSkill(BaseSkill):
    """更新昵称"""
    name = "update_nickname"
    description = "更新用户昵称"
    params_model = UpdateNicknameParams

    # ✅ 改为纯异步
    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncUserService(db)
                user = await service.update_nickname(args.user_id, args.nickname)
                return {"code": 0, "data": {"nickname": user.nickname}}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetUserAddressesSkill(BaseSkill):
    """获取用户地址"""
    name = "get_user_addresses"
    description = "获取用户收货地址列表"
    params_model = GetUserAddressesParams

    # ✅ 改为纯异步
    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.user_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncUserService(db)
                data = await service.get_addresses(args.user_id)
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, args.user_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

USER_SKILL_CLS = [
    GetUserProfileSkill,
    UpdateNicknameSkill,
    GetUserAddressesSkill
]