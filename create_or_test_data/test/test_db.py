import os
import sys
# 强制使用utf-8编码
sys.stdout.reconfigure(encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"
from sqlalchemy import text
from database.db import engine, get_db

print("1.数据库文件路径：", engine.url.database)
print("2.运行目录：", os.getcwd())


db = next(get_db())
sql = text("SELECT name FROM sqlite_master WHERE type='table';")
tables = db.execute(sql).fetchall()
print("3.库内数据表：", [t[0] for t in tables])
