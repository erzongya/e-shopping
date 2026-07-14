from chromadb import PersistentClient
from utils.llm_factory import get_embedding_model
from config.settings import settings
# 创建本地持久化向量库实例，数据存在配置指定文件夹
client = PersistentClient(path=settings.VECTOR_STORE_ROOT)
# 获取/创建 goods_vector_collection
goods_collection = client.get_or_create_collection("goods_vector_collection")
embedding_model = get_embedding_model()

def add_goods_vector(goods_id: str, content: str):
    # 1. 把商品描述文字翻译成向量数组
    vec = embedding_model.embed_query(content)
    # 2. 塞进商品向量盒子
    goods_collection.add(ids=[goods_id], embeddings=[vec], documents=[content])

def search_goods_vector(query: str, top_k: int = 3):
    # 1. 用户提问文字，同样翻译成向量
    vec = embedding_model.embed_query(query)
    # 2. 在盒子里对比所有向量，找出距离最近top3个
    result = goods_collection.query(query_embeddings=[vec], n_results=top_k)
    return result