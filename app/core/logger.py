# common/logger.py
"""
日志模块 - 适配项目结构

功能：
1. 支持链路追踪（trace_id / session_id）
2. 自动脱敏（手机号、身份证）
3. 环境区分（dev/prod）
4. 按天轮转，保留14天
5. 错误日志单独记录
6. 线程安全的单例模式
"""
import logging
import os
import re
import traceback
from logging.handlers import TimedRotatingFileHandler
from threading import Lock
from typing import Optional

from app.core.settings import settings, BASE_DIR

# ==================== 常量 ====================

LOG_DIR = "logs"
LOG_FILE = "app.log"
ERROR_FILE = "error.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "trace_id=%(trace_id)s | session_id=%(session_id)s | "
    "msg=%(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ROTATE_WHEN = "midnight"  # 每天午夜轮转
ROTATE_INTERVAL = 1
BACKUP_COUNT = 14
LOG_ENCODING = "utf-8"

# 脱敏正则（预编译提升性能）
PHONE_PATTERN = re.compile(r"(1[3-9]\d)\d{4}(\d{4})")
ID_CARD_PATTERN = re.compile(r"(\d{6})\d{8}(\d{4})")



# ==================== 工具函数 ====================

def desensitize(text: str) -> str:
    """
    日志脱敏：手机号、身份证

    例：
        13812345678 -> 138****5678
        110101199001011234 -> 110101********1234
    """
    if not isinstance(text, str):
        text = str(text)
    text = PHONE_PATTERN.sub(r"\1****\2", text)
    text = ID_CARD_PATTERN.sub(r"\1********\2", text)
    return text


def ensure_log_dir() -> str:
    """确保日志目录存在"""
    log_path = os.path.join(BASE_DIR, LOG_DIR)
    if not os.path.exists(log_path):
        os.makedirs(log_path, mode=0o755)
        print(f"[LOG] 创建日志目录: {log_path}")
    return log_path


# ==================== 日志单例管理器 ====================

class LoggerManager:
    """日志管理器 - 线程安全的单例"""

    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._init_logger()
        self._initialized = True

    def _init_logger(self):
        """初始化日志器（只执行一次）"""
        # 1. 创建日志目录
        log_path = ensure_log_dir()

        # 2. 创建日志器
        self.logger = logging.getLogger("ecommerce")
        self.logger.propagate = False
        self.logger.handlers.clear()

        self.logger.setLevel(logging.INFO)
        console_level = logging.INFO
        print("【LOG】日志系统初始化完成")
        # 4. 日志格式
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        # 5. 控制台 Handler
        console = logging.StreamHandler()
        console.setLevel(console_level)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # 6. 文件 Handler（按天轮转）
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_path, LOG_FILE),
            when=ROTATE_WHEN,
            interval=ROTATE_INTERVAL,
            backupCount=BACKUP_COUNT,
            encoding=LOG_ENCODING
        )
        file_handler.setLevel(logging.DEBUG if settings.ENV == "dev" else logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 7. 错误日志 Handler（单独文件）
        error_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_path, ERROR_FILE),
            when=ROTATE_WHEN,
            interval=ROTATE_INTERVAL,
            backupCount=BACKUP_COUNT,
            encoding=LOG_ENCODING
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def get_logger(self) -> logging.Logger:
        """获取日志器"""
        return self.logger


# ==================== 全局实例 ====================

_logger_manager = LoggerManager()
_logger = _logger_manager.get_logger()


# ==================== 对外 API ====================

def log_info(trace_id: str, session_id: str, msg: str) -> None:
    """记录 INFO 日志"""
    _logger.info(
        desensitize(msg),
        extra={"trace_id": trace_id or "", "session_id": session_id or ""}
    )


def log_debug(trace_id: str, session_id: str, msg: str) -> None:
    """记录 DEBUG 日志（仅开发环境生效）"""
    if settings.ENV == "dev":
        _logger.debug(
            desensitize(msg),
            extra={"trace_id": trace_id or "", "session_id": session_id or ""}
        )


def log_warning(trace_id: str, session_id: str, msg: str) -> None:
    """记录 WARNING 日志"""
    _logger.warning(
        desensitize(msg),
        extra={"trace_id": trace_id or "", "session_id": session_id or ""}
    )


def log_error(trace_id: str, session_id: str, msg: str, error: Optional[Exception] = None) -> None:
    """记录 ERROR 日志（自动记录堆栈）"""
    if error:
        _logger.error(
            desensitize(msg),
            extra={"trace_id": trace_id or "", "session_id": session_id or ""},
            exc_info=True
        )
    else:
        _logger.error(
            desensitize(msg),
            extra={"trace_id": trace_id or "", "session_id": session_id or ""}
        )

