"""
JWT 鉴权工具
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Header, status
from app.core.settings import settings

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============ 密码相关 ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


# ============ JWT 相关 ============

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict:
    """解析 JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============ 依赖注入 ============

async def get_current_user(
        authorization: str = Header(..., alias="Authorization")
) -> Dict:
    """
    从 Authorization Header 解析当前用户
    用法：在接口中 current_user = Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization 格式错误，应为 Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
    }


async def get_current_user_optional(
        authorization: str = Header(None, alias="Authorization")
) -> Optional[Dict]:
    """
    可选鉴权：有 Token 就解析，没有就返回 None
    用于公开接口 + 登录接口
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

