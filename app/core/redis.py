# app/core/redis.py
"""
Redis 连接管理 - 企业级
"""
import redis.asyncio as redis
from typing import Optional
import json
from app.core.logger import log_info, log_error
from app.core.settings import settings


class RedisClient:
    """Redis 客户端 - 单例"""

    _instance = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> redis.Redis:
        if self._client is not None:
            return self._client

        self._client = redis.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=False,
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        await self._client.ping()
        log_info("", "redis", "✅ Redis 连接成功")
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None
            log_info("", "redis", "🔄 Redis 已关闭")

    async def get(self, key: str) -> Optional[str]:
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int = 300):
        await self._client.setex(key, ttl, value)

    async def delete(self, key: str):
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._client.exists(key) > 0


redis_client = RedisClient()


# ==================== 便捷函数 ====================

async def get_redis():
    return await redis_client.connect()


async def set_cache(key: str, value, ttl: int = 300):
    """设置缓存"""
    client = await get_redis()
    await client.setex(key, ttl, json.dumps(value))


async def get_cache(key: str):
    """获取缓存"""
    client = await get_redis()
    data = await client.get(key)
    return json.loads(data) if data else None


async def delete_cache(key: str):
    """删除缓存"""
    client = await get_redis()
    await client.delete(key)


async def clear_cache(pattern: str = "*"):
    """清空缓存"""
    client = await get_redis()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)