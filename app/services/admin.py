"""
管理后台业务逻辑 - 异步版
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from app.models.admin import Admin, AdminLog
from app.common.exceptions import BusinessException, NotFoundException, UnauthorizedException
from app.core.security import hash_password, verify_password


class AsyncAdminService:
    """管理后台服务 - 异步"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 认证相关 ==========

    async def login(self, username: str, password: str, ip: str = "") -> Dict[str, Any]:
        """管理员登录"""
        result = await self.db.execute(
            select(Admin).where(
                Admin.username == username,
                Admin.status == 1
            )
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise NotFoundException("管理员", username)

        if not verify_password(password, admin.password_hash):
            raise BusinessException("密码错误")

        admin.last_login_time = datetime.now()
        admin.last_login_ip = ip
        await self.db.commit()
        await self.db.refresh(admin)

        await self.log_operation(
            admin_id=admin.id,
            action="login",
            content=f"管理员登录成功",
            ip=ip
        )

        return {
            "id": admin.id,
            "username": admin.username,
            "real_name": admin.real_name,
            "role": admin.role,
            "last_login_time": admin.last_login_time
        }

    async def change_password(self, admin_id: str, old_password: str, new_password: str) -> bool:
        """修改密码"""
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            raise NotFoundException("管理员", admin_id)

        if not verify_password(old_password, admin.password_hash):
            raise BusinessException("原密码错误")

        admin.password_hash = hash_password(new_password)
        await self.db.commit()

        await self.log_operation(
            admin_id=admin_id,
            action="change_password",
            content="修改密码"
        )

        return True

    # ========== 管理员管理 ==========

    async def create_admin(
        self,
        username: str,
        password: str,
        real_name: str = "",
        phone: str = "",
        email: str = "",
        role: str = "operator"
    ) -> Admin:
        """创建管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.username == username)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise BusinessException(f"用户名 {username} 已存在")

        admin = Admin(
            username=username,
            password_hash=hash_password(password),
            real_name=real_name or username,
            phone=phone,
            email=email,
            role=role
        )

        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)

        return admin

    async def get_admin(self, admin_id: str) -> Dict[str, Any]:
        """获取管理员信息"""
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            raise NotFoundException("管理员", admin_id)

        return {
            "id": admin.id,
            "username": admin.username,
            "real_name": admin.real_name,
            "phone": admin.phone,
            "email": admin.email,
            "role": admin.role,
            "status": admin.status,
            "created_at": admin.created_at,
            "last_login_time": admin.last_login_time
        }

    async def list_admins(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取管理员列表"""
        query = select(Admin)
        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(desc(Admin.created_at)).offset(offset).limit(page_size)
        )
        admins = result.scalars().all()

        return {
            "list": [{
                "id": a.id,
                "username": a.username,
                "real_name": a.real_name,
                "role": a.role,
                "status": a.status,
                "last_login_time": a.last_login_time,
                "created_at": a.created_at
            } for a in admins],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_admin_status(self, admin_id: str, status: int) -> Admin:
        """更新管理员状态"""
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            raise NotFoundException("管理员", admin_id)

        admin.status = status
        await self.db.commit()
        await self.db.refresh(admin)

        return admin

    async def delete_admin(self, admin_id: str) -> bool:
        """删除管理员（软删除，置为冻结）"""
        return await self.update_admin_status(admin_id, 2)

    # ========== 操作日志 ==========

    async def log_operation(
        self,
        admin_id: str,
        action: str,
        content: str = "",
        target: str = "",
        target_id: str = "",
        ip: str = "",
        user_agent: str = ""
    ) -> AdminLog:
        """记录操作日志"""
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            content=content,
            target=target,
            target_id=target_id,
            ip=ip,
            user_agent=user_agent
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_logs(
        self,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取操作日志"""
        query = select(AdminLog)

        if admin_id:
            query = query.where(AdminLog.admin_id == admin_id)
        if action:
            query = query.where(AdminLog.action == action)

        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(desc(AdminLog.created_at)).offset(offset).limit(page_size)
        )
        logs = result.scalars().all()

        return {
            "list": [{
                "id": l.id,
                "admin_id": l.admin_id,
                "action": l.action,
                "target": l.target,
                "target_id": l.target_id,
                "content": l.content,
                "ip": l.ip,
                "created_at": l.created_at
            } for l in logs],
            "total": total,
            "page": page,
            "page_size": page_size
        }