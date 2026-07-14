from vector_store.store import search_goods_vector


query = "蓝牙"
print("传入搜索文本：", query, type(query))
data = search_goods_vector(query)
print("向量检索结果：", data)

