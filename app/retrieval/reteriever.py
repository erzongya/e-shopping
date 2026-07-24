from typing import List, Tuple
from langchain_core.documents import Document
from app.retrieval.vector_store import vector_store

class Retriever:
    """检索器"""

    # RAG 触发关键词
    RAG_KEYWORDS = [
        "规则", "政策", "说明", "怎么办", "如何", "流程",
        "退货", "退款", "换货", "运费", "保修", "售后",
        "7天", "无理由", "运费险", "保障", "服务", "规定"
    ]

    @staticmethod
    def search(query: str, top_k: int = 3) -> Tuple[List[Document], str]:
        """检索并返回格式化上下文"""
        docs = vector_store.search(query, top_k=top_k)
        context = vector_store.format_context(docs)
        return docs, context

    @staticmethod
    def is_relevant(query) -> bool:
        """判断问题是否与知识库相关"""
        # 处理各种输入类型
        if query is None:
            return False
        if isinstance(query, list):
            # 如果是列表，取第一个元素
            if not query:
                return False
            # 如果第一个元素是字典（消息格式），提取 text
            if isinstance(query[0], dict):
                query = query[0].get("text", "") or query[0].get("content", "") or ""
            else:
                query = str(query[0])
        elif not isinstance(query, str):
            query = str(query)

        query_lower = query.lower()
        for keyword in Retriever.RAG_KEYWORDS:
            if keyword in query_lower:
                return True
        return False