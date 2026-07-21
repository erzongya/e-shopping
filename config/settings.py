# 配置文件

from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()
# 获取项目根目录（settings.py所在文件夹的上一层 = 项目根）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # 环境模式
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
    REDIS_HOST:str
    REDIS_PORT:int
    REDIS_DB:int
    CHECKPOINT_KEY_PREFIX:str
    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == "prod"

    @property
    def DB_URL(self):
        """数据库路径"""
        db_file = os.path.join(BASE_DIR, "data", "ecom.db")
        return f"sqlite:///{db_file}"

    @property
    def VECTOR_STORE_ROOT(self):
        """向量库存放目录绝对路径"""
        return os.path.join(BASE_DIR, "data", "vector_store")

settings = Settings()
if __name__ == '__main__':
    print(settings)
