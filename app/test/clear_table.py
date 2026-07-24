import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base  # 这里替换成你实际定义模型的文件名

# 直接用你确认过的数据库连接字符串
DATABASE_URL = "postgresql+asyncpg://root:123456@localhost:5432/mydatabase"
async_engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True 会打印SQL日志

async def init_db():
    async with async_engine.begin() as conn:
        # 这会打印建表的SQL语句，非常有助于调试
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")

if __name__ == "__main__":
    asyncio.run(init_db())