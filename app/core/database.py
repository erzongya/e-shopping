"""
异步数据库配置 PostgreSQL + asyncpg
1. 性能极高：是目前最快的 PostgreSQL Python 驱动
2. 原生异步：完美支持 FastAPI 的异步架构
3. 连接池：内置连接池管理，支持高并发
4. 类型安全：自动映射 PostgreSQL 数据类型
"""

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from typing import AsyncGenerator
from app.core.settings import settings
from app.models.base import Base
# ==================== 创建异步引擎 ====================
async_engine = create_async_engine(
    settings.DATABASE_URL,     # PostgreSQL 连接地址
    echo=False,       # 开发环境打印 SQL
    pool_size=20,              # 连接池大小：20 个常驻连接
    max_overflow=40,           # 最大溢出：额外 40 个连接
    pool_pre_ping=True,        # 使用前检查连接是否有效
    pool_recycle=3600,         # 1 小时回收连接
)
# ==================== 创建异步会话工厂 ====================
"""
异步会话工厂配置说明：
- bind: 绑定的引擎
- class_: 会话类（使用 AsyncSession）
- expire_on_commit: 提交后是否过期对象
- autocommit: 是否自动提交（关闭，手动控制事务）
- autoflush: 是否自动刷新（关闭，手动控制）
"""
AsyncSessionLocal = async_sessionmaker(
    async_engine,              # 绑定的引擎
    class_=AsyncSession,       # 会话类（使用 AsyncSession）
    expire_on_commit=False,    # 提交后不过期对象
    autocommit=False,          # 是否自动提交
    autoflush=False,           # 是否自动刷新
)

# ==================== 基类 ====================
"""
所有模型继承此基类，用于创建表
"""

# ==================== 初始化数据库 ====================
async def init_db():
    """
    初始化数据库：创建所有表
    注意：生产环境建议使用 Alembic 迁移工具
    """
    # ========== 添加这行调试代码 ==========
    print(">>> 调试：Base 中已注册的模型表名：", list(Base.metadata.tables.keys()))
    # =====================================
    async with async_engine.begin() as conn:
        # run_sync 用于在异步中执行同步操作
        await conn.run_sync(Base.metadata.create_all)
        print("【DB】PostgreSQL 数据库表初始化完成")


# ==================== 依赖注入 ====================
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（FastAPI 依赖注入）
    使用方式：
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    特点：
        1. 每次请求创建一个新会话
        2. 请求结束后自动关闭会话
        3. 支持事务管理
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ==================== 上下文管理器 ====================
