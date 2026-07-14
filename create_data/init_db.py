# 写入数据库引擎
from database.db import engine
# 导入数据表基类（包含所有表元数据）
from db.base import Base
import db.models
#日志打印
from utils.logger import logger

def create_tables():
    # 扫描所有继承Base的数据模型，不存在则自动创建数据表
    Base.metadata.create_all(bind=engine)
    logger.info("所有数据表创建完成,数据库文件生成成功")

# 脚本执行入口
if __name__ == "__main__":
    create_tables()