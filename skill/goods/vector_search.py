from skill.base import SkillParams,BaseSkill
from vector_store.store import search_goods_vector
class SearchSimilarGoodsParams(SkillParams):
    query: str
    top_k: int = 3

class SearchSimilarGoodsSkill(BaseSkill):
    name = "search_similar_goods"
    description = "根据用户自然语言描述，语义检索相似商品ID"
    params_model = SearchSimilarGoodsParams

    def run(self, **kwargs):
        try:
            # 兼容LLM错误传参格式
            # 1. 取出嵌套在kwargs字段里的实际参数
            if 'kwargs' in kwargs:
                import json
                kwargs = json.loads(kwargs['kwargs']) if isinstance(kwargs['kwargs'], str) else kwargs['kwargs']
            # 2. 兼容参数名为keyword的情况
            if 'keyword' in kwargs and 'query' not in kwargs:
                kwargs['query'] = kwargs.pop('keyword')

            args = self.params_model(**kwargs)
            res = search_goods_vector(args.query, args.top_k)
            ids = res['ids'][0]
            return ids
        except Exception as e:
            return f"工具异常：{str(e)}"