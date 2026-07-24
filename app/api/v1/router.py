"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, goods, chat

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(user.router, prefix="/user", tags=["用户"])
api_router.include_router(goods.router, prefix="/goods", tags=["商品"])
# api_router.include_router(order.router, prefix="/order", tags=["订单"])
# api_router.include_router(cart.router, prefix="/cart", tags=["购物车"])
# api_router.include_router(promotion.router, prefix="/promotion", tags=["促销"])
# api_router.include_router(aftersale.router, prefix="/aftersale", tags=["售后"])
# api_router.include_router(admin.router, prefix="/admin", tags=["管理"])
# api_router.include_router(ops.router, prefix="/ops", tags=["运营"])
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])