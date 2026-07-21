import logging
import os
import re
import traceback
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
from threading import Lock
from config.settings import settings, BASE_DIR

# ==================== 常量 ====================
LOG_DIR_NAME = "logs"
ERROR_LOG_NAME = "error.log"
LOG_ROTATE_INTERVAL = 1
LOG_BACKUP_DAYS = 14
LOG_ENCODING = "utf-8"
LOGGER_NAME = "ecommerce_agent"

LOG_PATH = os.path.join(BASE_DIR, LOG_DIR_NAME)
ERROR_LOG_FILE = os.path.join(LOG_PATH, ERROR_LOG_NAME)

print(f"[LOG CONFIG] BASE_DIR = {BASE_DIR}")
print(f"[LOG CONFIG] LOG_PATH = {LOG_PATH}")

# ==================== 全局锁 + 初始化标记（核心防重复） ====================
_INIT_LOCK = Lock()
_IS_LOG_INITIALIZED = False

# ==================== 创建日志目录 ====================
def init_log_dir() -> None:
    try:
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH, mode=0o755)
            print(f"[LOG CONFIG] 创建日志目录成功: {LOG_PATH}")
    except Exception as err:
        traceback.print_exc()
        raise RuntimeError(f"日志目录创建失败: {err}") from err

init_log_dir()

# ==================== 预编译脱敏正则 ====================
PHONE_PATTERN = re.compile(r"(1[3-9]\d)\d{4}(\d{4})")
ID_CARD_PATTERN = re.compile(r"(\d{6})\d{8}(\d{4})")

def safe_desensitize(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = PHONE_PATTERN.sub(r"\1****\2", text)
    text = ID_CARD_PATTERN.sub(r"\1********\2", text)
    return text

# ==================== 初始化logger（加锁只执行一次） ====================
def get_logger():
    global _IS_LOG_INITIALIZED
    logger = logging.getLogger(LOGGER_NAME)

    with _INIT_LOCK:
        # 已经初始化过，直接返回，不再新增handler
        if _IS_LOG_INITIALIZED:
            return logger

        # 清空已有handler
        logger.handlers.clear()

        # 设置日志等级
        if settings.ENV == "dev":
            global_level = logging.DEBUG
            console_level = logging.DEBUG
            print("【LOG ENV】开发环境：控制台输出DEBUG及以上")
        else:
            global_level = logging.INFO
            console_level = logging.ERROR
            print("【LOG ENV】生产环境：控制台仅输出ERROR")

        logger.setLevel(global_level)
        logger.propagate = False  # 禁止日志向上传递到根logger，双重打印元凶之一

        log_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | trace_id=%(trace_id)s | session_id=%(session_id)s | stack=%(stack)s | msg=%(message)s"
        )

        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(console_level)
        logger.addHandler(console_handler)

        # 错误文件handler
        file_handler = TimedRotatingFileHandler(
            filename=ERROR_LOG_FILE,
            when="D",
            interval=LOG_ROTATE_INTERVAL,
            backupCount=LOG_BACKUP_DAYS,
            encoding=LOG_ENCODING
        )
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

        # 标记初始化完成
        _IS_LOG_INITIALIZED = True
    return logger

# 拿到全局logger实例
_root_logger = get_logger()

# ==================== 对外工具函数 ====================
def log_info(trace_id: str, session_id: str, msg: str) -> None:
    safe_msg = safe_desensitize(msg)
    _root_logger.info(
        safe_msg,
        extra={
            "trace_id": trace_id,
            "session_id": session_id,
            "stack": ""
        }
    )

def log_error(trace_id: str, session_id: str, msg: str, err: Optional[Exception] = None) -> None:
    safe_msg = safe_desensitize(msg)
    stack_info = ""
    if err is not None:
        stack_info = "".join(traceback.format_exception(type(err), err, err.__traceback__)).strip()
    _root_logger.error(
        safe_msg,
        extra={
            "trace_id": trace_id,
            "session_id": session_id,
            "stack": stack_info
        }
    )

# 自测
if __name__ == "__main__":
    log_info("test_trace", "test_sid", "测试日志 手机号13812341111")
    try:
        1 / 0
    except Exception as e:
        log_error("test_trace", "test_sid", "测试异常", e)