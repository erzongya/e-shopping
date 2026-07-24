from enum import IntEnum

class OrderStatus(IntEnum):
    """订单状态"""
    PENDING = 1      # 待支付
    PAID = 2         # 已支付
    SHIPPED = 3      # 已发货
    COMPLETED = 4    # 已完成
    CANCELLED = 5    # 已取消
    REFUNDING = 6    # 退款中
    REFUNDED = 7     # 已退款

class AfterSaleStatus(IntEnum):
    """售后状态"""
    PENDING = 1      # 待审核
    APPROVED = 2     # 审核通过
    REJECTED = 3     # 审核拒绝
    RETURNING = 4    # 退货中
    COMPLETED = 5    # 已完成
    CLOSED = 6       # 已关闭


class AdminRole(IntEnum):
    """管理员角色"""
    SUPER_ADMIN = 1   # 超级管理员
    ADMIN = 2         # 管理员
    OPERATOR = 3      # 运营


class AdminStatus(IntEnum):
    """管理员状态"""
    ACTIVE = 1        # 正常
    FROZEN = 2        # 冻结