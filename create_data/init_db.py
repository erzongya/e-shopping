from database.db import engine
from db.base import Base

def create_all_tables():
    # 自动创建所有数据表
    Base.metadata.create_all(bind=engine)
    print("✅ 全部数据表创建完成！")

if __name__ == "__main__":
    create_all_tables()