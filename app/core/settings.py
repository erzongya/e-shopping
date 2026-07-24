# 配置文件

from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()
# 获取项目根目录（settings.py所在文件夹的上一层 = 项目根）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"BASE_DIR = {BASE_DIR}")
class Settings(BaseSettings):
    # 环境模式
    APP_NAME:str = "E-shoping"
    APP_VERSION:str = "1.0.0"
    model_config = SettingsConfigDict(extra="ignore")
    ENV: Literal["dev", "prod"] = os.getenv("ENVIRONMENT", "dev")
    DEBUG: bool = os.getenv("DEBUG", "true") == "true"

    # 模型切换开关
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false") == "true"
    USE_LOCAL_EMBED: bool = os.getenv("USE_LOCAL_EMBED", "false") == "true"

    # 本地 Ollama 模型
    LOCAL_LLM_MODEL: str
    LOCAL_EMBED_MODEL: str

    # 线上 LLM 配置
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str

    # 线上 Embedding 配置
    EMBED_BASE_URL: str
    EMBED_API_KEY: str
    EMBED_MODEL: str

    # 服务配置
    HOST:str
    PORT:int
    REDIS_URL:str
    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == "prod"

    DATABASE_URL: str = "postgresql+asyncpg://root:123456@localhost:5432/mydatabase"
    # ==================== Redis ====================
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    @property
    def VECTOR_STORE_ROOT(self):
        """向量库存放目录绝对路径"""
        return os.path.join(BASE_DIR, "data", "vector_store")

    # ==================== JWT ====================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天


settings = Settings()
if __name__ == '__main__':
    print(settings)
