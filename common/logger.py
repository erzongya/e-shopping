import logging
import os
import traceback
from logging.handlers import TimedRotatingFileHandler
from config.settings import settings, BASE_DIR

# 日志路径
LOG_PATH = os.path.join(BASE_DIR, 'logs')
print(f"BASE_DIR = {BASE_DIR}")
print(f"LOG_PATH = {LOG_PATH}")

# 创建文件夹带打印
try:
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
except Exception as err:
    print("❌ 创建文件夹失败，错误详情：", repr(err))

ERROR_LOG_FILE = os.path.join(LOG_PATH, "error.log")

# 日志实例初始化
logger = logging.getLogger("agent")
# 彻底清空旧handler，避免缓存干扰
while logger.handlers:
    logger.handlers.pop()

# 全局日志等级
if settings.ENV == "dev":
    logger.setLevel(logging.DEBUG)
    print("✅ 全局等级 DEBUG")
else:
    logger.setLevel(logging.INFO)
    print("ℹ️ 全局等级 INFO")

# 原生文本格式，无第三方依赖
log_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | trace_id=%(trace_id)s | session_id=%(session_id)s | msg=%(message)s"
)

# 1. 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_fmt)
if settings.ENV == "dev":
    console_handler.setLevel(logging.DEBUG)
    print("✅ 控制台等级 DEBUG，info日志正常输出")
else:
    # 生产环境只打印错误
    console_handler.setLevel(logging.ERROR)
    print("ℹ️ 控制台等级 ERROR，屏蔽info日志")
logger.addHandler(console_handler)

# 2. 文件处理器：只存ERROR日志
file_handler = TimedRotatingFileHandler(
    filename=ERROR_LOG_FILE,
    when="D",
    interval=1,
    backupCount=14,
    encoding="utf-8"
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(log_fmt)
logger.addHandler(file_handler)

# 隐私脱敏
def safe_desensitize(text: str) -> str:
    import re
    text = re.sub(r"(1[3-9]\d)\d{4}(\d{4})", r"\1****\2", text)
    text = re.sub(r"(\d{6})\d{8}(\d{4})", r"\1********\2", text)
    return text

# 普通信息日志（仅控制台输出，不写入文件）
def log_info(trace_id: str, session_id: str, msg: str):
    msg = safe_desensitize(msg)
    logger.info(
        msg,
        extra={
            "trace_id": trace_id,
            "session_id": session_id,
            "stack": ""
        }
    )

# 错误日志（控制台+文件双存）
def log_error(trace_id: str, session_id: str, msg: str, err: Exception = None):
    msg = safe_desensitize(msg)
    stack_info = ""
    if err:
        stack_info = "".join(traceback.format_exception(type(err), err, err.__traceback__))
    logger.error(
        msg,
        extra={
            "trace_id": trace_id,
            "session_id": session_id,
            "stack": stack_info
        }
    )

# 自测入口，直接运行本文件测试
if __name__ == '__main__':
    print("=====开始测试日志=====")
    trace_id = "test_trace_001"
    session_id = "test_sid_999"
    # 测试info日志
    log_info(trace_id, session_id, "用户查询商品，手机号13812345678，身份证310101199001011234")
    # 测试错误日志
    try:
        num = 1 / 0
    except Exception as e:
        log_error(trace_id, session_id, "计算除数为0，系统异常", e)