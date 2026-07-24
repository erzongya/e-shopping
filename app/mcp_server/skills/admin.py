"""
管理后台 MCP 技能 - 异步版
"""
from typing import Dict, Any, Optional
from pydantic import Field

from app.mcp_server.skills.base import BaseSkill, SkillParams
from app.services.admin import AsyncAdminService
from app.core.database import AsyncSessionLocal
from app.core.logger import log_info, log_error


# ========== 参数模型 ==========

class AdminLoginParams(SkillParams):
    """管理员登录参数"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class CreateAdminParams(SkillParams):
    """创建管理员参数"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    real_name: str = Field("", description="真实姓名")
    phone: str = Field("", description="手机号")
    email: str = Field("", description="邮箱")
    role: str = Field("operator", description="角色: super_admin/admin/operator")


class GetAdminParams(SkillParams):
    """获取管理员信息参数"""
    admin_id: str = Field(description="管理员ID")


class ListAdminsParams(SkillParams):
    """获取管理员列表参数"""
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


class UpdateAdminStatusParams(SkillParams):
    """更新管理员状态参数"""
    admin_id: str = Field(description="管理员ID")
    status: int = Field(description="状态: 1正常 2冻结")


class GetLogsParams(SkillParams):
    """获取操作日志参数"""
    admin_id: Optional[str] = Field(None, description="管理员ID")
    action: Optional[str] = Field(None, description="操作类型")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


# ========== 技能实现 ==========

class AdminLoginSkill(BaseSkill):
    """管理员登录"""
    name = "admin_login"
    description = "管理员登录"
    params_model = AdminLoginParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "admin_login", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                result = await service.login(
                    username=args.username,
                    password=args.password
                )
                return {"code": 0, "data": result}
            except Exception as e:
                log_error(trace_id, "admin_login", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class CreateAdminSkill(BaseSkill):
    """创建管理员"""
    name = "create_admin"
    description = "创建管理员账号"
    params_model = CreateAdminParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "admin", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                admin = await service.create_admin(
                    username=args.username,
                    password=args.password,
                    real_name=args.real_name,
                    phone=args.phone,
                    email=args.email,
                    role=args.role
                )
                return {"code": 0, "data": {"id": admin.id, "username": admin.username}}
            except Exception as e:
                log_error(trace_id, "admin", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetAdminSkill(BaseSkill):
    """获取管理员信息"""
    name = "get_admin"
    description = "获取管理员信息"
    params_model = GetAdminParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.admin_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                data = await service.get_admin(args.admin_id)
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, args.admin_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class ListAdminsSkill(BaseSkill):
    """获取管理员列表"""
    name = "list_admins"
    description = "获取管理员列表"
    params_model = ListAdminsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "admin_list", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                data = await service.list_admins(
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, "admin_list", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class UpdateAdminStatusSkill(BaseSkill):
    """更新管理员状态"""
    name = "update_admin_status"
    description = "更新管理员状态（启用/冻结）"
    params_model = UpdateAdminStatusParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, args.admin_id, f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                admin = await service.update_admin_status(
                    admin_id=args.admin_id,
                    status=args.status
                )
                return {"code": 0, "data": {"id": admin.id, "status": admin.status}}
            except Exception as e:
                log_error(trace_id, args.admin_id, f"执行失败", e)
                return {"code": -1, "msg": str(e)}


class GetLogsSkill(BaseSkill):
    """获取操作日志"""
    name = "get_admin_logs"
    description = "获取管理员操作日志"
    params_model = GetLogsParams

    async def run(self, **kwargs) -> Dict[str, Any]:
        args = self.params_model(**kwargs)
        trace_id = self.context.get("trace_id", "")

        log_info(trace_id, "admin_logs", f"执行技能: {self.name}")

        async with AsyncSessionLocal() as db:
            try:
                service = AsyncAdminService(db)
                data = await service.get_logs(
                    admin_id=args.admin_id,
                    action=args.action,
                    page=args.page,
                    page_size=args.page_size
                )
                return {"code": 0, "data": data}
            except Exception as e:
                log_error(trace_id, "admin_logs", f"执行失败", e)
                return {"code": -1, "msg": str(e)}


# ========== 注册列表 ==========

ADMIN_SKILL_CLS = [
    AdminLoginSkill,
    CreateAdminSkill,
    GetAdminSkill,
    ListAdminsSkill,
    UpdateAdminStatusSkill,
    GetLogsSkill
]