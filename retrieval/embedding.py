from langchain_openai import OpenAIEmbeddings
from config.settings import settings



def get_embeddings():
    """获取 Embedding 模型"""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",  # 性价比最高
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )