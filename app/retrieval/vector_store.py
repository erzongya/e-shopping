# retrieval/vector_store.py
import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from app.common.llm_factory import get_embedding_model
from app.core.settings import settings, BASE_DIR

# ========== 路径配置 ==========

DOC_DIR = os.path.join(BASE_DIR, "retrieval", "documents")
PERSIST_DIR = settings.VECTOR_STORE_ROOT

class VectorStoreManager:
    """向量库管理器"""

    def __init__(self, collection_name: str = "ecom_knowledge"):
        self.collection_name = collection_name
        self.embeddings = get_embedding_model()
        self._store = None

    def get_store(self) -> Chroma:
        """获取向量库实例"""
        if self._store is None:
            os.makedirs(PERSIST_DIR, exist_ok=True)
            self._store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=PERSIST_DIR,
            )
        return self._store

    def load_documents(self, doc_dir: str = None):
        """加载知识文档并入库"""
        if doc_dir is None:
            doc_dir = DOC_DIR

        print(f"[RAG] 加载文档目录: {doc_dir}")

        if not os.path.exists(doc_dir):
            print(f"[RAG] ❌ 文档目录不存在: {doc_dir}")
            print(f"[RAG] 请创建目录: mkdir {doc_dir}")
            return 0

        store = self.get_store()

        # 读取所有 .txt 文档
        documents = []
        for filename in os.listdir(doc_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(doc_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={"source": filename}
                    ))

        if not documents:
            print("[RAG] ⚠️ 没有找到 .txt 文档")
            return 0

        # 分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )
        chunks = splitter.split_documents(documents)

        # 入库（新版 Chroma 会自动持久化）
        store.add_documents(chunks)
        # ❌ 删除这行：store.persist()

        print(f"[RAG] ✅ 已加载 {len(documents)} 个文档，分 {len(chunks)} 个块")
        return len(chunks)

    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """检索相关文档"""
        store = self.get_store()
        return store.similarity_search(query, k=top_k)

    def format_context(self, docs: List[Document]) -> str:
        """格式化检索结果为 Prompt 上下文"""
        if not docs:
            return ""

        context = "【知识库参考】\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            context += f"--- 参考{i}（来源：{source}）---\n"
            context += doc.page_content + "\n\n"

        return context


# 全局单例
vector_store = VectorStoreManager()