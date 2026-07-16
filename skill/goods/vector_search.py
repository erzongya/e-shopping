from skill.base import SkillParams, BaseSkill
from vector_store.store import search_goods_vector
from pydantic import Field

class SearchSimilarGoodsParams(SkillParams):
    """参数模型，所有参数平铺在args顶层，禁止使用kwargs嵌套包裹"""
    keyword: str = Field(
        description="商品搜索关键词，唯一核心入参，禁止使用query、kwargs字段"
    )
    top_k: int = Field(default=3, description="返回商品最大条数，非必填顶层参数")

class SearchSimilarGoodsSkill(BaseSkill):
    name = "search_similar_goods"
    description = "根据关键词搜索相似商品；keyword、top_k全部平铺在args顶层，禁止用kwargs打包嵌套参数"
    params_model = SearchSimilarGoodsParams

    def run(self, **kwargs):
        try:
            args = self.params_model(** kwargs)
            res = search_goods_vector(args.keyword, args.top_k)
            ids = res['ids'][0]
            return {
                "success": True,
                "code": 0,
                "msg": "商品检索成功",
                "data": ids
            }
        except Exception as e:
            # 移除异常里的kwargs关键词，避免污染对话记忆误导LLM循环输出错误格式
            template = '{"keyword": "搜索关键词", "top_k": 3}'
            return {
                "success": False,
                "code": 4001,
                "msg": f"参数格式错误，标准平铺格式：{template}，所有参数直接放在args顶层，错误详情：{str(e)}",
                "data": None
            }