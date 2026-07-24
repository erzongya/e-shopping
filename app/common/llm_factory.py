from app.core.settings import settings
def get_chat_llm(temperature: float = 0.1):
    """
    区分本地线上
    """
    if settings.USE_LOCAL_LLM:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.LOCAL_LLM_MODEL,
            temperature=temperature
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            temperature=temperature
        )


def get_embedding_model():
    """
    统一获取向量模型实例
    自动切换 本地/线上，向量库始终保存在本地目录
    """
    if settings.USE_LOCAL_EMBED:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=settings.LOCAL_EMBED_MODEL)
    else:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=settings.EMBED_MODEL,
            api_key=settings.EMBED_API_KEY,
            base_url=settings.EMBED_BASE_URL,
            check_embedding_ctx_length=False,
            model_kwargs={"encoding_format": "float"}
        )