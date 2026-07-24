# app/services/user_async.py
"""
用户业务逻辑服务 - 异步版（FastAPI 使用）
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User, UserAddress
from app.common.exceptions import BusinessException, NotFoundException
from app.core.security import hash_password, verify_password


class AsyncUserService:
    """用户业务服务 - 异步（FastAPI 使用）"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户对象"""
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.status == 1
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(User).where(
                User.phone == phone,
                User.status == 1
            )
        )
        return result.scalar_one_or_none()

    async def register(self, phone: str, password: str, nickname: str = "") -> User:
        """
        用户注册

        Args:
            phone: 手机号
            password: 密码
            nickname: 昵称

        Returns:
            创建的用户对象
        """
        # 检查手机号是否已存在
        existing = await self.get_user_by_phone(phone)
        if existing:
            raise BusinessException(f"手机号 {phone} 已被注册")

        # 创建用户
        user = User(
            phone=phone,
            nickname=nickname or f"用户{phone[-4:]}",
            password_hash=hash_password(password)
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(self, phone: str, password: str) -> User:
        """
        用户登录

        Args:
            phone: 手机号
            password: 密码

        Returns:
            用户对象
        """
        user = await self.get_user_by_phone(phone)

        if not user:
            raise NotFoundException("用户不存在")

        if not verify_password(password, user.password_hash):
            raise BusinessException("密码错误")

        # 更新登录时间
        user.last_login_time = datetime.now()
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        user = await self.get_user_by_id(user_id)

        if not user:
            raise NotFoundException("用户不存在")

        return {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "vip_level": user.vip_level,
            "point": user.point,
            "total_spent": float(user.total_spent) if user.total_spent else 0.0,
            "register_time": user.register_time.strftime("%Y-%m-%d %H:%M:%S") if user.register_time else None
        }

    async def update_nickname(self, user_id: str, nickname: str) -> User:
        """更新昵称"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("用户不存在")

        user.nickname = nickname
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_addresses(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户地址列表"""
        result = await self.db.execute(
            select(UserAddress)
            .where(UserAddress.user_id == user_id)
            .order_by(UserAddress.is_default.desc())
        )
        addresses = result.scalars().all()

        return [{
            "id": a.id,
            "name": a.name,
            "phone": a.phone,
            "province": a.province,
            "city": a.city,
            "district": a.district,
            "address": a.address,
            "is_default": a.is_default
        } for a in addresses]

    async def add_address(
        self,
        user_id: str,
        name: str,
        phone: str,
        province: str,
        city: str,
        district: str,
        address: str,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """添加收货地址"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("用户不存在")

        # 如果设置为默认，取消其他默认地址
        if is_default:
            await self.db.execute(
                update(UserAddress)
                .where(
                    UserAddress.user_id == user_id,
                    UserAddress.is_default == True
                )
                .values(is_default=False)
            )

        address_obj = UserAddress(
            user_id=user_id,
            name=name,
            phone=phone,
            province=province,
            city=city,
            district=district,
            address=address,
            is_default=is_default
        )
        self.db.add(address_obj)
        await self.db.commit()
        await self.db.refresh(address_obj)

        return {
            "id": address_obj.id,
            "name": address_obj.name,
            "phone": address_obj.phone,
            "is_default": address_obj.is_default
        }

    async def delete_address(self, user_id: str, address_id: str) -> bool:
        """删除收货地址"""
        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundException("地址不存在")

        await self.db.delete(address)
        await self.db.commit()
        return True

    async def set_default_address(self, user_id: str, address_id: str) -> bool:
        """设置默认地址"""
        # 取消所有默认
        await self.db.execute(
            update(UserAddress)
            .where(
                UserAddress.user_id == user_id,
                UserAddress.is_default == True
            )
            .values(is_default=False)
        )

        # 设置新的默认
        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundException("地址不存在")

        address.is_default = True
        await self.db.commit()
        return True

    async def get_points(self, user_id: str) -> int:
        """获取用户积分"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("用户不存在")
        return user.point