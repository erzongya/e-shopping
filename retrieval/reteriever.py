from typing import List, Tuple
from langchain_core.documents import Document
from retrieval.vector_store import vector_store

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
    def is_relevant(query: str) -> bool:
        """判断问题是否与知识库相关"""
        query_lower = query.lower()
        for keyword in Retriever.RAG_KEYWORDS:
            if keyword in query_lower:
                return True
        return False