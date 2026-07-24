# scripts/seed_real_data.py
"""
生成真实感测试数据 - 异步版
运行方式：python scripts/seed_real_data.py
"""
import sys
import os
import random
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# ✅ 导入所有模型（必须在数据库连接之前）
# ============================================
from app.models import (
    User, UserAddress, Goods, GoodsSpec, GoodsComment, GoodsCategory,
    Order, OrderItem, OrderLog, Cart, Promotion, Coupon, UserCoupon,
    AfterSale, Admin, AdminLog, ChatSession, ChatHistory
)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.settings import settings
from app.core.security import hash_password

async_engine = create_async_engine(settings.DATABASE_URL, echo=False)
print(f"🔍 连接的数据库: {settings.DATABASE_URL}")

# ==================== 真实数据 ====================

BRANDS = ['Apple', '华为', '小米', '耐克', '阿迪达斯', 'SK-II', '雅诗兰黛', '周大福', '飞利浦', '美的']

GOODS_NAMES = {
    '电子产品': ['iPhone 15 Pro Max', '华为Mate 60 Pro', '小米14 Ultra', 'AirPods Pro 2', 'MacBook Air M3'],
    '服装': ['Nike Air Force 1', 'Adidas Ultraboost', "Levi's 501牛仔裤", '优衣库羽绒服', 'ZARA西装外套'],
    '食品': ['三只松鼠坚果礼盒', '良品铺子零食大礼包', '星巴克咖啡豆', '德芙巧克力礼盒', '五常大米'],
    '家居': ['宜家沙发', '双立人刀具套装', '戴森吸尘器', '小米扫地机器人', '飞利浦空气炸锅'],
    '图书': ['三体全集', '人类简史', '深度工作', '金字塔原理', '原则'],
    '美妆': ['SK-II神仙水', '雅诗兰黛小棕瓶', '兰蔻粉水', 'YSL口红', '阿玛尼粉底液']
}

NICKNAMES = ['张三', '李四', '王五', '赵六', 'Alice', 'Bob', 'Charlie', 'David', 'Eva', 'Frank',
             '小明', '小红', '小刚', '小丽', '小华', '小强', '小芳', '小军', '小敏', '小涛']

CITIES = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '成都市', '武汉市', '西安市', '南京市', '重庆市']
DISTRICTS = ['朝阳区', '浦东新区', '天河区', '南山区', '西湖区', '武侯区', '洪山区', '雁塔区', '鼓楼区', '渝中区']
STREETS = ['中关村大街', '陆家嘴环路', '体育西路', '科技园路', '文一路', '天府大道', '珞喻路', '长安路', '中山路', '解放碑']

PHONE_PREFIXES = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                  '150', '151', '152', '153', '155', '156', '157', '158', '159',
                  '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']

PROMOTIONS = [
    {'name': '618年中大促', 'type': 1, 'min_amount': 300, 'discount_amount': 50},
    {'name': '双11狂欢节', 'type': 1, 'min_amount': 500, 'discount_amount': 100},
    {'name': '开学季特惠', 'type': 2, 'min_amount': 200, 'discount_rate': 0.88},
    {'name': '会员专享8折', 'type': 2, 'min_amount': 150, 'discount_rate': 0.80},
    {'name': '新人首单优惠', 'type': 1, 'min_amount': 100, 'discount_amount': 30},
]

COUPONS = [
    {'name': '满100减20', 'type': 1, 'min_amount': 100, 'discount_amount': 20},
    {'name': '满200减50', 'type': 1, 'min_amount': 200, 'discount_amount': 50},
    {'name': '8折优惠券', 'type': 2, 'min_amount': 150, 'discount_rate': 0.80, 'max_discount': 100},
    {'name': '满300减80', 'type': 1, 'min_amount': 300, 'discount_amount': 80},
    {'name': '9折券', 'type': 2, 'min_amount': 100, 'discount_rate': 0.90, 'max_discount': 50},
]

COMMENTS = [
    '非常满意，质量很好，物流也很快！',
    '性价比很高，推荐购买！',
    '和描述一致，做工精致。',
    '包装完好，产品很赞。',
    '客服服务态度很好，问题及时解决。',
    '有点小失望，没有想象中好。',
    '品质不错，值得信赖的品牌。',
    '物流很快，第二天就到了。',
    '价格实惠，质量也不错。',
    '外观漂亮，功能齐全。',
    '尺寸合适，穿着舒适。',
    '味道很好，日期新鲜。',
]

CHAT_MESSAGES = [
    '你好，我想咨询一下商品信息',
    '这个商品有保修吗？',
    '快递什么时候能到？',
    '可以退货吗？',
    '价格还能优惠吗？',
    '好的，我知道了，谢谢',
    '我想买这个，怎么下单？',
    '有现货吗？',
    '可以开发票吗？',
    '支持货到付款吗？'
]

AI_RESPONSES = [
    '您好！很高兴为您服务。这个商品有1年保修期。',
    '快递通常在3-5天内送达。',
    '支持7天无理由退货。',
    '目前是活动价格，已经很优惠了。',
    '有现货，下单后立即发货。',
    '好的，有什么问题随时联系我们。',
    '点击立即购买即可下单。',
    '现货充足，可以放心购买。',
    '可以开电子发票，下单时备注即可。',
    '支持在线支付，暂不支持货到付款。'
]


def random_phone():
    return random.choice(PHONE_PREFIXES) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

def random_price(min_val=10, max_val=5000):
    return round(random.uniform(min_val, max_val), 2)

def random_past_date(max_days: int = 365):
    return datetime.now() - timedelta(days=random.randint(0, max_days))

def random_future_date(max_days: int = 30):
    return datetime.now() + timedelta(days=random.randint(1, max_days))

def get_category():
    return random.choice(list(GOODS_NAMES.keys()))

def get_goods_name(category):
    return random.choice(GOODS_NAMES.get(category, ['商品']))


async def seed_all():
    print("=" * 60)
    print("  📦 开始生成真实测试数据")
    print("=" * 60)

    async with async_engine.begin() as conn:
        # ==================== 1. 用户 (20个) ====================
        print("\n👤 生成用户...")
        users = []
        for i in range(20):
            nickname = random.choice(NICKNAMES) + str(random.randint(100, 999))
            result = await conn.execute(
                text("""
                    INSERT INTO "user" (
                        id, phone, nickname, password_hash, avatar, email, 
                        vip_level, vip_expire_time, point, total_spent, 
                        status, register_time, last_login_time, last_login_ip,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :phone, :nickname, :password_hash, :avatar, :email,
                        :vip_level, :vip_expire_time, :point, :total_spent,
                        :status, :register_time, :last_login_time, :last_login_ip,
                        NOW(), NOW()
                    ) RETURNING id
                """),
                {
                    "phone": random_phone(),
                    "nickname": nickname,
                    "password_hash": hash_password("123456"),
                    "avatar": f"https://i.pravatar.cc/150?img={i + 1}",
                    "email": f"{nickname.lower()}@example.com",
                    "vip_level": random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.25, 0.2, 0.1, 0.05])[0],
                    "vip_expire_time": random_future_date(365) if random.random() > 0.3 else None,
                    "point": random.randint(0, 5000),
                    "total_spent": random_price(100, 10000),
                    "status": random.choices([1, 2, 3], weights=[0.85, 0.1, 0.05])[0],
                    "register_time": random_past_date(365),
                    "last_login_time": random_past_date(7),
                    "last_login_ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                }
            )
            users.append(result.scalar())
            if (i + 1) % 5 == 0:
                print(f"  ✅ 已生成 {i + 1} 个用户")
        print(f"  ✅ 总共生成 {len(users)} 个用户")

        # ==================== 2. 收货地址 ====================
        print("\n📮 生成收货地址...")
        addresses = []
        for user_id in users[:15]:
            for i in range(random.randint(1, 3)):
                result = await conn.execute(
                    text("""
                        INSERT INTO user_address (
                            id, user_id, name, phone, province, city, district, address, is_default,
                            created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), :user_id, :name, :phone, :province, :city, :district, :address, :is_default,
                            NOW(), NOW()
                        )
                        RETURNING id
                    """),
                    {
                        "user_id": user_id,
                        "name": random.choice(['张先生', '李女士', '王先生', '刘女士', '陈先生']),
                        "phone": random_phone(),
                        "province": random.choice(['北京市', '上海市', '广东省', '浙江省', '四川省']),
                        "city": random.choice(CITIES),
                        "district": random.choice(DISTRICTS),
                        "address": f"{random.choice(STREETS)} {random.randint(1, 999)}号 {random.choice(['小区', '花园', '广场'])} {random.randint(1, 30)}栋{random.randint(1, 20)}室",
                        "is_default": (i == 0)
                    }
                )
                addresses.append(result.scalar())
        print(f"  ✅ 生成 {len(addresses)} 个地址")

        # ==================== 3. 商品分类 ====================
        print("\n📂 生成商品分类...")
        cat_map = {}
        cats = [
            {'name': '电子产品', 'level': 1},
            {'name': '服装', 'level': 1},
            {'name': '食品', 'level': 1},
            {'name': '家居', 'level': 1},
            {'name': '图书', 'level': 1},
            {'name': '美妆', 'level': 1},
            {'name': '手机', 'parent': '电子产品', 'level': 2},
            {'name': '电脑', 'parent': '电子产品', 'level': 2},
            {'name': '男装', 'parent': '服装', 'level': 2},
            {'name': '女装', 'parent': '服装', 'level': 2},
            {'name': '零食', 'parent': '食品', 'level': 2},
            {'name': '生鲜', 'parent': '食品', 'level': 2},
        ]
        for cat in cats:
            parent_id = "00000000-0000-0000-0000-000000000000"
            if 'parent' in cat and cat['parent'] in cat_map:
                parent_id = cat_map[cat['parent']]
            result = await conn.execute(
                text("""
                    INSERT INTO goods_category (
                        id, name, parent_id, level, sort, icon, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :name, :parent_id, :level, :sort, :icon, NOW(), NOW()
                    ) RETURNING id
                """),
                {
                    "name": cat['name'],
                    "parent_id": parent_id,
                    "level": cat['level'],
                    "sort": random.randint(0, 100),
                    "icon": f"https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/{random.randint(1, 100)}.png"
                }
            )
            cat_map[cat['name']] = result.scalar()
        print(f"  ✅ 生成 {len(cats)} 个分类")

        # ==================== 4. 商品 (30个) ====================
        print("\n📦 生成商品...")
        goods_ids = []
        for i in range(30):
            category = get_category()
            name = get_goods_name(category)
            price = random_price(50, 5000)
            is_flash = random.choices([0, 1], weights=[0.7, 0.3])[0]

            result = await conn.execute(
                text("""
                    INSERT INTO goods (
                        id, name, category, sub_category, brand, price, flash_price, cost_price,
                        stock, sold_count, view_count, "desc", images, is_flash,
                        flash_limit, buy_limit, flash_end_time, is_hot, is_new, is_recommend, status,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :name, :category, :sub_category, :brand, :price, :flash_price, :cost_price,
                        :stock, :sold_count, :view_count, :desc, :images, :is_flash,
                        :flash_limit, :buy_limit, :flash_end_time, :is_hot, :is_new, :is_recommend, :status,
                        NOW(), NOW()
                    ) RETURNING id
                """),
                {
                    "name": f"{name} {random.choice(['旗舰版', '标准版', 'Pro', 'Max', '青春版', '尊享版'])}",
                    "category": category,
                    "sub_category": random.choice(['高端', '中端', '入门']),
                    "brand": random.choice(BRANDS),
                    "price": price,
                    "flash_price": round(price * random.uniform(0.5, 0.8), 2) if is_flash else 0.00,
                    "cost_price": round(price * random.uniform(0.4, 0.7), 2),
                    "stock": random.randint(0, 500),
                    "sold_count": random.randint(0, 5000),
                    "view_count": random.randint(0, 10000),
                    "desc": f"这是一款高品质的{name}，采用最新技术，品质优良。{random.choice(['用户好评如潮', '销量领先', '值得信赖'])}",
                    "images": f"https://picsum.photos/seed/{i + 1}/400/400",
                    "is_flash": is_flash,
                    "flash_limit": random.randint(1, 5) if is_flash else 1,
                    "buy_limit": random.randint(5, 20),
                    "flash_end_time": random_future_date(30) if is_flash else None,
                    "is_hot": random.choice([True, False]),
                    "is_new": random.choice([True, False]),
                    "is_recommend": random.choice([True, False]),
                    "status": random.choices([1, 2], weights=[0.85, 0.15])[0]
                }
            )
            goods_ids.append(result.scalar())
            if (i + 1) % 10 == 0:
                print(f"  ✅ 已生成 {i + 1} 个商品")
        print(f"  ✅ 总共生成 {len(goods_ids)} 个商品")

        # ==================== 5. 商品规格 ====================
        print("\n🔧 生成商品规格...")
        spec_count = 0
        spec_names = ['颜色', '尺寸', '容量', '材质']
        spec_values = {
            '颜色': ['红色', '蓝色', '黑色', '白色', '金色', '银色'],
            '尺寸': ['S', 'M', 'L', 'XL', 'XXL'],
            '容量': ['128GB', '256GB', '512GB', '1TB'],
            '材质': ['纯棉', '涤纶', '羊毛', '丝绸', '皮革']
        }
        for goods_id in goods_ids[:20]:
            spec_name = random.choice(spec_names)
            values = spec_values.get(spec_name, ['标准'])
            for value in random.sample(values, min(3, len(values))):
                await conn.execute(
                    text("""
                        INSERT INTO goods_spec (
                            id, goods_id, spec_name, spec_value, spec_price, spec_stock, spec_image,
                            created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), :goods_id, :spec_name, :spec_value, :spec_price, :spec_stock, :spec_image,
                            NOW(), NOW()
                        )
                    """),
                    {
                        "goods_id": goods_id,
                        "spec_name": spec_name,
                        "spec_value": value,
                        "spec_price": random_price(10, 300),
                        "spec_stock": random.randint(0, 100),
                        "spec_image": f"https://picsum.photos/seed/spec_{spec_count}/200/200"
                    }
                )
                spec_count += 1
        print(f"  ✅ 生成 {spec_count} 个规格")

        # ==================== 6. 商品评论 ====================
        print("\n💬 生成商品评论...")
        comment_count = 0
        for goods_id in goods_ids[:15]:
            for _ in range(random.randint(0, 5)):
                if random.random() > 0.4:
                    user_id = random.choice(users[:10])
                    await conn.execute(
                        text("""
                            INSERT INTO goods_comment (
                                id, goods_id, user_id, content, score, tag, images, is_anonymous, status,
                                created_at, updated_at
                            ) VALUES (
                                gen_random_uuid(), :goods_id, :user_id, :content, :score, :tag, :images, :is_anonymous, :status,
                                :created_at, NOW()
                            )
                        """),
                        {
                            "goods_id": goods_id,
                            "user_id": user_id,
                            "content": random.choice(COMMENTS),
                            "score": random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.08, 0.15, 0.35, 0.37])[0],
                            "tag": random.choice(['质量好', '物流快', '性价比高', '服务好', '尺寸合适']),
                            "images": "https://picsum.photos/seed/comment/200/200" if random.random() > 0.7 else None,
                            "is_anonymous": random.choice([True, False]),
                            "status": random.choices([1, 2], weights=[0.9, 0.1])[0],
                            "created_at": random_past_date(180)
                        }
                    )
                    comment_count += 1
        print(f"  ✅ 生成 {comment_count} 条评论")

        # ==================== 7. 订单 ====================
        print("\n📋 生成订单...")
        order_count = 0
        statuses = [1, 2, 3, 4, 5, 6, 7]
        status_weights = [0.1, 0.2, 0.15, 0.3, 0.05, 0.1, 0.1]

        for user_id in users[:15]:
            for _ in range(random.randint(1, 5)):
                total = random_price(50, 2000)
                status = random.choices(statuses, weights=status_weights)[0]
                pay_time = random_past_date(30) if status >= 2 else None

                await conn.execute(
                    text("""
                        INSERT INTO "order" (
                            id, order_no, user_id, total_amount, discount_amount, freight_amount, pay_amount,
                            status, pay_method, pay_time, pay_transaction_id,
                            receiver_name, receiver_phone, receiver_province, receiver_city, receiver_district, receiver_address,
                            logistics_company, logistics_no, ship_time, confirm_time,
                            user_remark, created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), :order_no, :user_id, :total_amount, :discount_amount, :freight_amount, :pay_amount,
                            :status, :pay_method, :pay_time, :pay_transaction_id,
                            :receiver_name, :receiver_phone, :receiver_province, :receiver_city, :receiver_district, :receiver_address,
                            :logistics_company, :logistics_no, :ship_time, :confirm_time,
                            :user_remark, :created_at, NOW()
                        )
                    """),
                    {
                        "order_no": f"ORD{datetime.now().strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                        "user_id": user_id,
                        "total_amount": total,
                        "discount_amount": round(total * random.uniform(0, 0.2), 2),
                        "freight_amount": 10.00 if total < 99 else 0.00,
                        "pay_amount": round(total * random.uniform(0.7, 0.95), 2),
                        "status": status,
                        "pay_method": random.choice(['wechat', 'alipay', 'balance']) if status >= 2 else None,
                        "pay_time": pay_time,
                        "pay_transaction_id": f"TXN{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}" if status >= 2 else None,
                        "receiver_name": random.choice(['张先生', '李女士', '王先生']),
                        "receiver_phone": random_phone(),
                        "receiver_province": random.choice(['北京市', '上海市', '广东省']),
                        "receiver_city": random.choice(CITIES),
                        "receiver_district": random.choice(DISTRICTS),
                        "receiver_address": f"{random.choice(STREETS)} {random.randint(1, 999)}号",
                        "logistics_company": random.choice(['顺丰速运', '圆通快递', '中通快递', '京东物流']) if status >= 3 else None,
                        "logistics_no": f"SF{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}" if status >= 3 else None,
                        "ship_time": random_past_date(20) if status >= 3 else None,
                        "confirm_time": random_past_date(10) if status >= 4 else None,
                        "user_remark": random.choice(['', '请尽快发货', '注意包装', '周末送货']) if random.random() > 0.6 else '',
                        "created_at": random_past_date(90)
                    }
                )
                order_count += 1
        print(f"  ✅ 生成 {order_count} 个订单")

        # ==================== 8. 订单明细 ====================
        print("\n📄 生成订单明细...")
        item_count = 0
        orders_result = await conn.execute(text('SELECT id FROM "order"'))
        order_ids = [row[0] for row in orders_result.fetchall()]

        for order_id in order_ids[:50]:
            for _ in range(random.randint(1, 3)):
                goods_id = random.choice(goods_ids[:20])
                quantity = random.randint(1, 3)
                price = random_price(50, 2000)
                await conn.execute(
                    text("""
                        INSERT INTO order_item (
                            id, order_id, goods_id, goods_name, goods_image, spec_name,
                            price, quantity, total_amount, is_commented,
                            created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), :order_id, :goods_id, :goods_name, :goods_image, :spec_name,
                            :price, :quantity, :total_amount, :is_commented,
                            NOW(), NOW()
                        )
                    """),
                    {
                        "order_id": order_id,
                        "goods_id": goods_id,
                        "goods_name": f"商品_{random.randint(1, 100)}",
                        "goods_image": "https://picsum.photos/seed/item/200/200",
                        "spec_name": random.choice(['红色', 'M码', '256GB']) if random.random() > 0.5 else None,
                        "price": price,
                        "quantity": quantity,
                        "total_amount": price * quantity,
                        "is_commented": random.choice([True, False])
                    }
                )
                item_count += 1
        print(f"  ✅ 生成 {item_count} 个订单明细")

        # ==================== 9. 购物车 ====================
        print("\n🛒 生成购物车...")
        cart_count = 0
        for user_id in users[:12]:
            for goods_id in random.sample(goods_ids[:20], min(5, len(goods_ids[:20]))):
                if random.random() > 0.5:
                    await conn.execute(
                        text("""
                            INSERT INTO cart (
                                id, user_id, goods_id, spec_id, quantity, selected,
                                created_at, updated_at
                            ) VALUES (
                                gen_random_uuid(), :user_id, :goods_id, :spec_id, :quantity, :selected,
                                NOW(), NOW()
                            )
                        """),
                        {
                            "user_id": user_id,
                            "goods_id": goods_id,
                            "spec_id": None,
                            "quantity": random.randint(1, 3),
                            "selected": random.choice([True, False])
                        }
                    )
                    cart_count += 1
        print(f"  ✅ 生成 {cart_count} 个购物车项")

        # ==================== 10. 促销活动 ====================
        print("\n🎉 生成促销活动...")
        for promo in PROMOTIONS:
            await conn.execute(
                text("""
                    INSERT INTO promotion (
                        id, name, type, min_amount, discount_amount, discount_rate,
                        apply_type, apply_targets, start_time, end_time, status,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :name, :type, :min_amount, :discount_amount, :discount_rate,
                        :apply_type, :apply_targets, :start_time, :end_time, :status,
                        NOW(), NOW()
                    )
                """),
                {
                    "name": promo['name'],
                    "type": promo['type'],
                    "min_amount": promo.get('min_amount', 0),
                    "discount_amount": promo.get('discount_amount', 0),
                    "discount_rate": promo.get('discount_rate', 1.0),
                    "apply_type": random.choice([1, 2, 3]),
                    "apply_targets": '["1", "2"]' if random.random() > 0.5 else None,
                    "start_time": datetime.now() - timedelta(days=random.randint(0, 15)),
                    "end_time": datetime.now() + timedelta(days=random.randint(5, 60)),
                    "status": random.choices([1, 2, 3], weights=[0.15, 0.55, 0.3])[0]
                }
            )
        print(f"  ✅ 生成 {len(PROMOTIONS)} 个促销活动")

        # ==================== 11. 优惠券 ====================
        print("\n🎫 生成优惠券...")
        for coupon_data in COUPONS:
            await conn.execute(
                text("""
                    INSERT INTO coupon (
                        id, name, code, type, min_amount, discount_amount, discount_rate, max_discount,
                        start_time, end_time, stock, limit_per_user, used_count, status,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :name, :code, :type, :min_amount, :discount_amount, :discount_rate, :max_discount,
                        :start_time, :end_time, :stock, :limit_per_user, :used_count, :status,
                        NOW(), NOW()
                    )
                """),
                {
                    "name": coupon_data['name'],
                    "code": f"CP{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                    "type": coupon_data['type'],
                    "min_amount": coupon_data.get('min_amount', 0),
                    "discount_amount": coupon_data.get('discount_amount', 0),
                    "discount_rate": coupon_data.get('discount_rate', 1.0),
                    "max_discount": coupon_data.get('max_discount', 0),
                    "start_time": datetime.now() - timedelta(days=5),
                    "end_time": datetime.now() + timedelta(days=random.randint(10, 60)),
                    "stock": random.randint(50, 200),
                    "limit_per_user": random.randint(1, 3),
                    "used_count": random.randint(0, 30),
                    "status": 1
                }
            )
        print(f"  ✅ 生成 {len(COUPONS)} 个优惠券")

        # ==================== 12. 管理员 ====================
        print("\n👨‍💼 生成管理员...")
        admin_data = [
            {'username': 'admin', 'real_name': '超级管理员', 'role': 'super_admin'},
            {'username': 'manager', 'real_name': '张经理', 'role': 'admin'},
            {'username': 'operator', 'real_name': '李运营', 'role': 'operator'},
        ]
        for data in admin_data:
            await conn.execute(
                text("""
                    INSERT INTO admin (
                        id, username, password_hash, real_name, phone, email, role, status,
                        last_login_time, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :username, :password_hash, :real_name, :phone, :email, :role, :status,
                        :last_login_time, NOW(), NOW()
                    )
                """),
                {
                    "username": data['username'],
                    "password_hash": hash_password("123456"),
                    "real_name": data['real_name'],
                    "phone": random_phone(),
                    "email": f"{data['username']}@admin.com",
                    "role": data['role'],
                    "status": 1,
                    "last_login_time": random_past_date(3)
                }
            )
        print(f"  ✅ 生成 {len(admin_data)} 个管理员")

        # ==================== 13. 聊天 ====================
        print("\n💬 生成聊天数据...")
        chat_session_count = 0
        chat_msg_count = 0
        for user_id in users[:8]:
            for _ in range(random.randint(1, 3)):
                session_result = await conn.execute(
                    text("""
                        INSERT INTO chat_sessions (
                            id, user_id, title, created_at, updated_at, is_deleted
                        ) VALUES (
                            gen_random_uuid(), :user_id, :title, :created_at, NOW(), false
                        ) RETURNING id
                    """),
                    {
                        "user_id": user_id,
                        "title": f"对话_{random.randint(1, 100)}",
                        "created_at": random_past_date(30)
                    }
                )
                session_id = session_result.scalar()
                chat_session_count += 1

                for _ in range(random.randint(2, 6)):
                    user_msg_time = random_past_date(7)
                    await conn.execute(
                        text("""
                            INSERT INTO chat_history (
                                id, user_id, session_id, role, content, tokens_used, model,
                                created_at, updated_at
                            ) VALUES (
                                gen_random_uuid(), :user_id, :session_id, 'user', :content, :tokens_used, 'gpt-3.5-turbo',
                                :created_at, NOW()
                            )
                        """),
                        {
                            "user_id": user_id,
                            "session_id": session_id,
                            "content": random.choice(CHAT_MESSAGES),
                            "tokens_used": random.randint(10, 50),
                            "created_at": user_msg_time
                        }
                    )
                    chat_msg_count += 1

                    await conn.execute(
                        text("""
                            INSERT INTO chat_history (
                                id, user_id, session_id, role, content, tokens_used, model,
                                created_at, updated_at
                            ) VALUES (
                                gen_random_uuid(), :user_id, :session_id, 'assistant', :content, :tokens_used, 'gpt-3.5-turbo',
                                :created_at, NOW()
                            )
                        """),
                        {
                            "user_id": user_id,
                            "session_id": session_id,
                            "content": random.choice(AI_RESPONSES),
                            "tokens_used": random.randint(20, 100),
                            "created_at": user_msg_time + timedelta(seconds=random.randint(5, 60))
                        }
                    )
                    chat_msg_count += 1
        print(f"  ✅ 生成 {chat_session_count} 个聊天会话，{chat_msg_count} 条消息")

    print("\n" + "=" * 60)
    print("  🎉 所有测试数据生成完成！")
    print("=" * 60)
    print("\n📋 登录信息:")
    print("  管理员: admin / 123456")
    print("  用户密码: 123456")


if __name__ == "__main__":
    asyncio.run(seed_all())