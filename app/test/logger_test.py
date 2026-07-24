# test_create_table.py
import asyncio
from sqlalchemy import Column, String, Integer, DateTime, Numeric, SmallInteger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

# 1. 定义 Base
Base = declarative_base()

# 2. 定义一个最简单的测试模型
class TestUser(Base):
    __tablename__ = "test_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 3. 数据库连接（直接用你确认过的信息）
DATABASE_URL = "postgresql+asyncpg://root:123456@localhost:5432/mydatabase"
engine = create_async_engine(DATABASE_URL, echo=True)

async def create_tables():
    async with engine.begin() as conn:
        # 这里会打印 CREATE TABLE 的 SQL 语句
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 测试表创建完成")

if __name__ == "__main__":
    asyncio.run(create_tables())