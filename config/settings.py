# 配置文件

from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # 环境模式
    model_config = SettingsConfigDict(extra="ignore")
    ENVIRONMENT: Literal["dev", "prod"] = os.getenv("ENVIRONMENT", "dev")
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

    # 本地持久化存储（永久固定）
    DB_URL: str
    VECTOR_STORE_ROOT: str

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == "prod"

settings = Settings()
print(settings)