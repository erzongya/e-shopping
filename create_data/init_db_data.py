import uuid
from datetime import datetime
from database.db import SessionLocal
from db.goods_models import Goods, GoodsComment, GoodsSpec
from db.user_models import UserInfo, UserAddress, UserSignIn
from db.cart_models import UserCart
from db.promoption_models import ActivityCoupon, UserCoupon, ActivityFlash
from db.order_models import UserOrder, OrderLogistics
from db.aftersale_models import OrderRefund, ComplaintTicket, ManualTicket
from db.admin_models import AdminSalesStat


def insert_all_fake_data():
    db = SessionLocal()
    try:
        now = datetime.now()

        # ===================== 1. 用户数据（5个用户） =====================
        users = [
            UserInfo(
                id="user_001", nickname="数码小王", phone="13800138000",
                vip_level=3, point=1280, register_time=now
            ),
            UserInfo(
                id="user_002", nickname="居家李姐", phone="13900139000",
                vip_level=2, point=650, register_time=now
            ),
            UserInfo(
                id="user_003", nickname="学生小张", phone="13700137000",
                vip_level=1, point=120, register_time=now
            ),
            UserInfo(
                id="user_004", nickname="商务老陈", phone="13600136000",
                vip_level=5, point=9800, register_time=now
            ),
            UserInfo(
                id="user_005", nickname="美妆小美", phone="13500135000",
                vip_level=4, point=5200, register_time=now
            ),
        ]
        db.add_all(users)
        db.flush()

        # 用户地址（每人2条）
        addresses = [
            UserAddress(id=str(uuid.uuid4()), user_id="user_001", name="王", phone="13800138000", address="上海市嘉定区环城路100号"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_001", name="王", phone="13800138000", address="苏州市工业园区星湖街88号"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_002", name="李", phone="13900139000", address="上海市普陀区长寿路200号"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_002", name="李", phone="13900139000", address="杭州市西湖区教工路50号"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_003", name="张", phone="13700137000", address="南京市鼓楼区汉口路22号"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_004", name="陈", phone="13600136000", address="北京市朝阳区建国门外大街"),
            UserAddress(id=str(uuid.uuid4()), user_id="user_005", name="美", phone="13500135000", address="广州市天河区天河路385号"),
        ]
        db.add_all(addresses)

        # 签到数据
        sign_list = [
            UserSignIn(id=str(uuid.uuid4()), user_id="user_001", sign_date="2026-07-18", reward_point=10, create_time=now),
            UserSignIn(id=str(uuid.uuid4()), user_id="user_001", sign_date="2026-07-19", reward_point=10, create_time=now),
            UserSignIn(id=str(uuid.uuid4()), user_id="user_002", sign_date="2026-07-19", reward_point=10, create_time=now),
            UserSignIn(id=str(uuid.uuid4()), user_id="user_003", sign_date="2026-07-20", reward_point=10, create_time=now),
        ]
        db.add_all(sign_list)
        db.flush()

        # ===================== 2. 商品数据（8个商品，覆盖秒杀/普通） =====================
        goods_data = [
            {
                "id": "goods_001",
                "name": "主动降噪无线蓝牙耳机",
                "category": "数码3C-耳机",
                "price": 199.00,
                "flash_price": 129.00,
                "stock": 320,
                "desc": "40dB深度降噪，24小时续航，支持无线快充",
                "is_flash": 1,
                "flash_limit": 2,
                "buy_limit": 5,
                "flash_end_time": datetime.strptime("2026-07-30 23:59:59", "%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "goods_002",
                "name": "家用大容量风冷冰箱",
                "category": "家电-冰箱",
                "price": 2499.00,
                "flash_price": 2199.00,
                "stock": 86,
                "desc": "320L容量，一级能效，分区保鲜，低噪节能",
                "is_flash": 0,
                "flash_limit": 1,
                "buy_limit": 2,
                "flash_end_time": None
            },
            {
                "id": "goods_003",
                "name": "20000mAh 大容量充电宝",
                "category": "数码配件",
                "price": 79.00,
                "flash_price": 49.90,
                "stock": 520,
                "desc": "双向快充，轻薄便携，多设备兼容",
                "is_flash": 1,
                "flash_limit": 3,
                "buy_limit": 10,
                "flash_end_time": datetime.strptime("2026-07-25 23:59:59", "%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "goods_004",
                "name": "机械电竞键盘青轴",
                "category": "电脑外设",
                "price": 159.00,
                "flash_price": 109.00,
                "stock": 210,
                "desc": "全键热插拔，RGB灯光，电竞专用",
                "is_flash": 1,
                "flash_limit": 2,
                "buy_limit": 3,
                "flash_end_time": datetime.strptime("2026-07-28 23:59:59", "%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "goods_005",
                "name": "夏季纯棉宽松T恤",
                "category": "服饰",
                "price": 59.90,
                "flash_price": 39.90,
                "stock": 999,
                "desc": "透气纯棉，不起球，多色可选",
                "is_flash": 0,
                "flash_limit": 0,
                "buy_limit": 20,
                "flash_end_time": None
            },
            {
                "id": "goods_006",
                "name": "智能扫地机器人",
                "category": "智能家居",
                "price": 1299.00,
                "flash_price": 999.00,
                "stock": 45,
                "desc": "自动回充、扫拖一体、智能避障",
                "is_flash": 1,
                "flash_limit": 1,
                "buy_limit": 1,
                "flash_end_time": datetime.strptime("2026-08-01 23:59:59", "%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "goods_007",
                "name": "高清手机钢化膜",
                "category": "手机配件",
                "price": 19.90,
                "flash_price": 9.90,
                "stock": 2000,
                "desc": "防指纹、防摔、高清透光",
                "is_flash": 0,
                "flash_limit": 0,
                "buy_limit": 50,
                "flash_end_time": None
            },
            {
                "id": "goods_008",
                "name": "人体工学办公椅",
                "category": "家居",
                "price": 399.00,
                "flash_price": 299.00,
                "stock": 68,
                "desc": "护腰靠背、可躺可升降、静音滚轮",
                "is_flash": 0,
                "flash_limit": 0,
                "buy_limit": 2,
                "flash_end_time": None
            },
        ]
        goods_list = [Goods(**g) for g in goods_data]
        db.add_all(goods_list)
        db.flush()

        # 商品规格（每个商品 1~2 条规格）
        spec_list = [
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_001", spec_name="黑色标准版", spec_price=0.00, spec_stock=150),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_001", spec_name="白色Pro版", spec_price=30.00, spec_stock=170),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_003", spec_name="白色2万毫安", spec_price=0.00, spec_stock=300),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_003", spec_name="黑色2万毫安", spec_price=0.00, spec_stock=220),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_004", spec_name="黑色青轴", spec_price=0.00, spec_stock=110),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_004", spec_name="白色红轴", spec_price=20.00, spec_stock=100),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_005", spec_name="M码", spec_price=0.00, spec_stock=300),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_005", spec_name="L码", spec_price=0.00, spec_stock=350),
            GoodsSpec(id=str(uuid.uuid4()), goods_id="goods_005", spec_name="XL码", spec_price=0.00, spec_stock=349),
        ]
        db.add_all(spec_list)
        db.flush()

        # 商品大量评论（多好评、中评、差评）
        comment_list = [
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_001", content="降噪超级好用，通勤地铁完全静音", tag="质量", score=5, create_time=datetime.strptime("2026-07-10 08:20:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_001", content="续航很强，一周充一次电足够用", tag="续航", score=5, create_time=datetime.strptime("2026-07-12 09:10:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_001", content="音质一般，性价比还行", tag="性价比", score=3, create_time=datetime.strptime("2026-07-13 15:40:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_001", content="收到有轻微划痕，介意慎拍", tag="品控", score=2, create_time=datetime.strptime("2026-07-14 11:20:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_002", content="容量很大，制冷效果不错", tag="质量", score=5, create_time=datetime.strptime("2026-07-11 16:30:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_003", content="充电很快，体积小巧", tag="性价比", score=5, create_time=datetime.strptime("2026-07-15 10:00:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_004", content="按键手感清脆，打游戏很爽", tag="体验", score=5, create_time=datetime.strptime("2026-07-16 19:20:00", "%Y-%m-%d %H:%M:%S")),
            GoodsComment(id=str(uuid.uuid4()), goods_id="goods_005", content="面料舒服，尺码标准", tag="质量", score=4, create_time=datetime.strptime("2026-07-17 14:10:00", "%Y-%m-%d %H:%M:%S")),
        ]
        db.add_all(comment_list)
        db.flush()

        # ===================== 3. 购物车数据（多用户多商品） =====================
        cart_list = [
            UserCart(id=str(uuid.uuid4()), user_id="user_001", goods_id="goods_001", spec_id=spec_list[0].id, buy_num=1, is_checked=1, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_001", goods_id="goods_003", spec_id=spec_list[2].id, buy_num=2, is_checked=0, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_002", goods_id="goods_002", spec_id=None, buy_num=1, is_checked=0, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_002", goods_id="goods_005", spec_id=spec_list[6].id, buy_num=3, is_checked=1, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_003", goods_id="goods_004", spec_id=spec_list[4].id, buy_num=1, is_checked=1, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_004", goods_id="goods_006", spec_id=None, buy_num=1, is_checked=0, create_time=now),
            UserCart(id=str(uuid.uuid4()), user_id="user_005", goods_id="goods_007", spec_id=None, buy_num=5, is_checked=1, create_time=now),
        ]
        db.add_all(cart_list)
        db.flush()

        # ===================== 4. 优惠券 + 用户领取 =====================
        coupon_list = [
            ActivityCoupon(id="coupon_001", coupon_name="满100减30通用券", full_limit=100, discount=30, total_limit=5000, receive_count=1200, expire_time=datetime.strptime("2026-12-31 23:59:59", "%Y-%m-%d %H:%M:%S"), need_point=0),
            ActivityCoupon(id="coupon_002", coupon_name="满200减50券", full_limit=200, discount=50, total_limit=3000, receive_count=890, expire_time=datetime.strptime("2026-11-30 23:59:59", "%Y-%m-%d %H:%M:%S"), need_point=0),
            ActivityCoupon(id="coupon_003", coupon_name="满2000减300家电券", full_limit=2000, discount=300, total_limit=800, receive_count=210, expire_time=datetime.strptime("2026-08-31 23:59:59", "%Y-%m-%d %H:%M:%S"), need_point=0),
            ActivityCoupon(id="coupon_004", coupon_name="10元无门槛券", full_limit=0, discount=10, total_limit=10000, receive_count=6500, expire_time=datetime.strptime("2026-09-30 23:59:59", "%Y-%m-%d %H:%M:%S"), need_point=0),
            ActivityCoupon(id="coupon_005", coupon_name="积分兑换5元券", full_limit=50, discount=5, total_limit=2000, receive_count=320, expire_time=datetime.strptime("2026-10-30 23:59:59", "%Y-%m-%d %H:%M:%S"), need_point=50),
        ]
        db.add_all(coupon_list)

        user_coupon_list = [
            UserCoupon(id=str(uuid.uuid4()), user_id="user_001", activity_id="coupon_001", is_used=0, create_time=now),
            UserCoupon(id=str(uuid.uuid4()), user_id="user_001", activity_id="coupon_004", is_used=1, create_time=now),
            UserCoupon(id=str(uuid.uuid4()), user_id="user_002", activity_id="coupon_003", is_used=0, create_time=now),
            UserCoupon(id=str(uuid.uuid4()), user_id="user_003", activity_id="coupon_004", is_used=0, create_time=now),
            UserCoupon(id=str(uuid.uuid4()), user_id="user_004", activity_id="coupon_002", is_used=0, create_time=now),
            UserCoupon(id=str(uuid.uuid4()), user_id="user_005", activity_id="coupon_005", is_used=0, create_time=now),
        ]
        db.add_all(user_coupon_list)

        # 秒杀活动
        flash_list = [
            ActivityFlash(id=str(uuid.uuid4()), goods_id="goods_001", flash_start=datetime.strptime("2026-07-20 00:00:00", "%Y-%m-%d %H:%M:%S"), flash_end=datetime.strptime("2026-07-30 23:59:59", "%Y-%m-%d %H:%M:%S"), stock_total=320),
            ActivityFlash(id=str(uuid.uuid4()), goods_id="goods_003", flash_start=datetime.strptime("2026-07-15 00:00:00", "%Y-%m-%d %H:%M:%S"), flash_end=datetime.strptime("2026-07-25 23:59:59", "%Y-%m-%d %H:%M:%S"), stock_total=520),
            ActivityFlash(id=str(uuid.uuid4()), goods_id="goods_004", flash_start=datetime.strptime("2026-07-18 00:00:00", "%Y-%m-%d %H:%M:%S"), flash_end=datetime.strptime("2026-07-28 23:59:59", "%Y-%m-%d %H:%M:%S"), stock_total=210),
        ]
        db.add_all(flash_list)
        db.flush()

        # ===================== 5. 大量订单 + 物流 =====================
        order_list = [
            UserOrder(id="order_001", user_id="user_001", goods_id="goods_001", spec_id=spec_list[0].id, order_no="ORD202607190001", buy_num=1, pay_price=129.00, status="运输中", tracking_no="SF1234567890", create_time=datetime.strptime("2026-07-19 09:30:00", "%Y-%m-%d %H:%M:%S")),
            UserOrder(id="order_002", user_id="user_001", goods_id="goods_003", spec_id=spec_list[2].id, order_no="ORD202607180002", buy_num=2, pay_price=99.80, status="已完成", tracking_no="YT9876543210", create_time=datetime.strptime("2026-07-18 14:20:00", "%Y-%m-%d %H:%M:%S")),
            UserOrder(id="order_003", user_id="user_002", goods_id="goods_002", spec_id=None, order_no="ORD202607170003", buy_num=1, pay_price=2199.00, status="待发货", tracking_no=None, create_time=datetime.strptime("2026-07-17 20:10:00", "%Y-%m-%d %H:%M:%S")),
            UserOrder(id="order_004", user_id="user_003", goods_id="goods_004", spec_id=spec_list[4].id, order_no="ORD202607160004", buy_num=1, pay_price=109.00, status="已完成", tracking_no="JD5678123400", create_time=datetime.strptime("2026-07-16 11:00:00", "%Y-%m-%d %H:%M:%S")),
            UserOrder(id="order_005", user_id="user_004", goods_id="goods_006", spec_id=None, order_no="ORD202607150005", buy_num=1, pay_price=999.00, status="已取消", tracking_no=None, create_time=datetime.strptime("2026-07-15 16:40:00", "%Y-%m-%d %H:%M:%S")),
            UserOrder(id="order_006", user_id="user_005", goods_id="goods_007", spec_id=None, order_no="ORD202607140006", buy_num=5, pay_price=49.50, status="已完成", tracking_no="ZT1122334455", create_time=datetime.strptime("2026-07-14 09:20:00", "%Y-%m-%d %H:%M:%S")),
        ]
        db.add_all(order_list)
        db.flush()

        # 物流轨迹
        log_list = [
            OrderLogistics(id=str(uuid.uuid4()), tracking_no="SF1234567890", track_time=datetime.strptime("2026-07-19 10:20:00", "%Y-%m-%d %H:%M:%S"), track_info="商品仓库打包出库"),
            OrderLogistics(id=str(uuid.uuid4()), tracking_no="SF1234567890", track_time=datetime.strptime("2026-07-19 18:10:00", "%Y-%m-%d %H:%M:%S"), track_info="已到达上海转运中心"),
            OrderLogistics(id=str(uuid.uuid4()), tracking_no="SF1234567890", track_time=datetime.strptime("2026-07-20 08:10:00", "%Y-%m-%d %H:%M:%S"), track_info="正在派送中，快递员正在上门"),
            OrderLogistics(id=str(uuid.uuid4()), tracking_no="YT9876543210", track_time=datetime.strptime("2026-07-18 16:00:00", "%Y-%m-%d %H:%M:%S"), track_info="已签收，订单完成"),
        ]
        db.add_all(log_list)

        # ===================== 6. 售后、退款、投诉、人工工单 =====================
        refund_list = [
            OrderRefund(id=str(uuid.uuid4()), user_id="user_001", order_id="order_002", refund_type="only_refund", reason="多余购买，不需要了", refund_amount=99.80, status="pass", create_time=now),
            OrderRefund(id=str(uuid.uuid4()), user_id="user_002", order_id="order_003", refund_type="return_refund", reason="想换更大容量型号", refund_amount=2199.00, status="pending", create_time=now),
            OrderRefund(id=str(uuid.uuid4()), user_id="user_003", order_id="order_004", refund_type="only_refund", reason="按键卡顿有问题", refund_amount=109.00, status="reject", create_time=now),
        ]
        db.add_all(refund_list)

        complaint_list = [
            ComplaintTicket(id=str(uuid.uuid4()), user_id="user_001", order_id="order_001", complaint_type="破损", description="耳机外壳轻微磕碰，包装破损", status="pending", create_time=now),
            ComplaintTicket(id=str(uuid.uuid4()), user_id="user_003", order_id="order_004", complaint_type="发货慢", description="下单后两天才发货", status="pass", create_time=now),
            ComplaintTicket(id=str(uuid.uuid4()), user_id="user_005", order_id="order_006", complaint_type="服务差", description="客服回复太慢", status="close", create_time=now),
        ]
        db.add_all(complaint_list)

        manual_list = [
            ManualTicket(id=str(uuid.uuid4()), user_id="user_001", session_id="sess_001", status="wait", create_time=now),
            ManualTicket(id=str(uuid.uuid4()), user_id="user_002", session_id="sess_002", status="online", create_time=now),
            ManualTicket(id=str(uuid.uuid4()), user_id="user_003", session_id="sess_003", status="close", create_time=now),
        ]
        db.add_all(manual_list)

        # ===================== 7. 运营统计数据 =====================
        stat_list = [
            AdminSalesStat(id=str(uuid.uuid4()), stat_date="2026-07-18", order_total=45, turnover=8965.20, refund_rate=3.25, create_time=now),
            AdminSalesStat(id=str(uuid.uuid4()), stat_date="2026-07-19", order_total=62, turnover=12580.50, refund_rate=2.10, create_time=now),
            AdminSalesStat(id=str(uuid.uuid4()), stat_date="2026-07-20", order_total=28, turnover=5620.00, refund_rate=1.80, create_time=now),
        ]
        db.add_all(stat_list)

        db.commit()
        print("✅【超大批量全表测试数据插入成功】")
        print("✅ 用户/商品/规格/评论/购物车/优惠券/订单/物流/售后/投诉/工单/统计 全部灌满")

    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败：{str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    insert_all_fake_data()