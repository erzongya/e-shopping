# test/test_rag.py
from retrieval.vector_store import vector_store
from retrieval.reteriever import Retriever


def test_rag():
    print("=" * 50)
    print("1. 加载文档")
    print("=" * 50)
    vector_store.load_documents()

    print("\n" + "=" * 50)
    print("2. 测试检索")
    print("=" * 50)

    queries = [
        "7天无理由退货怎么操作？",
        "运费险是什么？",
        "帮我查一下订单"
    ]

    for q in queries:
        print(f"\n查询: {q}")

        # 判断是否相关
        relevant = Retriever.is_relevant(q)
        print(f"  是否走RAG: {relevant}")

        if relevant:
            docs, context = Retriever.search(q, top_k=2)
            print(f"  检索到: {len(docs)} 条")
            print(f"  上下文预览:\n{context[:300]}...")
        else:
            print("  → 不走RAG，走工具调用")


if __name__ == "__main__":
    test_rag()