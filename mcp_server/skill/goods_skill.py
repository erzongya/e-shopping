from mcp_server.skill.base import SkillParams, BaseSkill
from pydantic import Field
from database.db import SessionLocal
from db.goods_models import Goods, GoodsComment, GoodsSpec
from datetime import datetime
from common.logger import log_info, log_error

# ========== 参数模型 ==========
class QueryGoodsDetailParams(SkillParams):
    goods_id: str = Field(description="商品唯一ID")

class ListGoodsByFilterParams(SkillParams):
    category: str | None = Field(None, description="商品分类，不传查全部分类")
    min_price: float | None = Field(None, description="最低价格")
    max_price: float | None = Field(None, description="最高价格")
    is_flash: int | None = Field(None, description="1仅秒杀商品，0普通商品")

class QueryGoodsSpecParams(SkillParams):
    goods_id: str = Field(description="商品ID")

class QueryGoodsCommentParams(SkillParams):
    goods_id: str = Field(description="商品ID")

# ========== 查询商品详情 ==========
class QueryGoodsDetailSkill(BaseSkill):
    name = "query_goods_detail"
    description = "根据商品ID查询商品完整基础信息，含名称、价格、库存、活动截止时间"
    params_model = QueryGoodsDetailParams

    def run(self, **kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(**kwargs)
        goods_id = args.goods_id
        session_id = goods_id
        log_info(trace_id, session_id, f"执行工具{self.name}，goods_id={goods_id}")
        try:
            item = db.query(Goods).filter(Goods.id == args.goods_id).first()
            if not item:
                log_info(trace_id, session_id, f"商品{goods_id}不存在")
                return {"code": -1, "msg": "商品不存在"}
            data = {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "price": float(item.price),
                "flash_price": float(item.flash_price),
                "stock": item.stock,
                "desc": item.desc,
                "is_flash": item.is_flash,
                "flash_limit": item.flash_limit,
                "buy_limit": item.buy_limit,
                "flash_end_time": item.flash_end_time.strftime("%Y-%m-%d %H:%M:%S") if item.flash_end_time else None
            }
            log_info(trace_id, session_id, f"商品{goods_id}查询成功")
            return {"code": 0, "data": data}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询商品异常，goods_id={goods_id}", e)
            return {"code": -1, "msg": str(e)}
        finally:
            db.close()

# ========== 多条件筛选商品列表 ==========
class ListGoodsByFilterSkill(BaseSkill):
    name = "list_goods_by_filter"
    description = "按分类、价格区间、是否秒杀批量查询商品列表"
    params_model = ListGoodsByFilterParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        session_id = "goods_filter"
        log_info(trace_id, session_id, f"执行工具{self.name}，筛选条件:{args.model_dump()}")
        try:
            q = db.query(Goods)
            if args.category:
                q = q.filter(Goods.category == args.category)
            if args.min_price is not None:
                q = q.filter(Goods.price >= args.min_price)
            if args.max_price is not None:
                q = q.filter(Goods.price <= args.max_price)
            if args.is_flash is not None:
                q = q.filter(Goods.is_flash == args.is_flash)
            rows = q.all()
            res = []
            for r in rows:
                res.append({
                    "id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "price": float(r.price),
                    "flash_price": float(r.flash_price),
                    "stock": r.stock
                })
            log_info(trace_id, session_id, f"筛选商品完成，共{len(res)}条")
            return {"code":0, "list": res}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}筛选商品异常", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# ========== 查询商品规格 ==========
class QueryGoodsSpecSkill(BaseSkill):
    name = "query_goods_spec"
    description = "查询商品全部规格，规格加价、独立库存"
    params_model = QueryGoodsSpecParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        goods_id = args.goods_id
        session_id = goods_id
        log_info(trace_id, session_id, f"执行工具{self.name}，goods_id={goods_id}")
        try:
            specs = db.query(GoodsSpec).filter(GoodsSpec.goods_id == args.goods_id).all()
            arr = []
            for s in specs:
                arr.append({
                    "spec_id": s.id,
                    "spec_name": s.spec_name,
                    "spec_price": float(s.spec_price),
                    "spec_stock": s.spec_stock
                })
            log_info(trace_id, session_id, f"商品{goods_id}规格查询成功，共{len(arr)}条")
            return {"code":0, "spec_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询规格异常，goods_id={goods_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

# ========== 查询商品评论 ==========
class QueryGoodsCommentSkill(BaseSkill):
    name = "query_goods_comment"
    description = "查询商品全部用户评价，含评分、标签、内容"
    params_model = QueryGoodsCommentParams

    def run(self,** kwargs):
        db = SessionLocal()
        trace_id = ""
        args = self.params_model(** kwargs)
        goods_id = args.goods_id
        session_id = goods_id
        log_info(trace_id, session_id, f"执行工具{self.name}，goods_id={goods_id}")
        try:
            comments = db.query(GoodsComment).filter(GoodsComment.goods_id == args.goods_id).all()
            arr = []
            for c in comments:
                arr.append({
                    "comment_id": c.id,
                    "content": c.content,
                    "tag": c.tag,
                    "score": c.score,
                    "create_time": c.create_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            log_info(trace_id, session_id, f"商品{goods_id}评论查询成功，共{len(arr)}条")
            return {"code":0, "comment_list": arr}
        except Exception as e:
            db.rollback()
            log_error(trace_id, session_id, f"工具{self.name}查询评论异常，goods_id={goods_id}", e)
            return {"code":-1, "msg":str(e)}
        finally:
            db.close()

GOODS_SKILL_CLS = [
    QueryGoodsDetailSkill,
    ListGoodsByFilterSkill,
    QueryGoodsSpecSkill,
    QueryGoodsCommentSkill
]