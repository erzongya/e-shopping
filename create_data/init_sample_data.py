from database.db import SessionLocal
from db.models import Goods
from services.goods_sevice import get_all_goods
from vector_store.store import add_goods_vector
from utils.logger import logger

#测试商品数据
sample_goods = [
    {"name":"主动降噪蓝牙耳机","price":199,"stock":50,"category":"数码","desc":"24小时续航，高清通话安卓苹果通用"},
    {"name":"纯棉短袖T恤","price":59,"stock":200,"category":"服饰","desc":"夏季宽松透气男女同款"},
    {"name":"20000毫安快充充电宝","price":89,"stock":36,"category":"数码","desc":"便携超薄支持PD快充"}
]

def insert_sample_data():
    db = SessionLocal()
    #先判断是否已有数据，避免重复插入
    exist = db.query(Goods).count()
    if exist > 0:
        logger.info("商品数据已存在，无需重复初始化")
        db.close()
        return

    #插入商品
    for item in sample_goods:
        db.add(Goods(**item))
    db.commit()
    logger.info("测试商品数据插入完成")

    # 批量生成商品描述向量存入向量库
    goods_list = get_all_goods(db)
    for g in goods_list:
        vec_text = f"{g.name} {g.category} {g.desc} 价格{g.price}元"
        add_goods_vector(str(g.id), vec_text)
    logger.info("全部商品向量入库完成")
    db.close()

if __name__ == '__main__':
    insert_sample_data()