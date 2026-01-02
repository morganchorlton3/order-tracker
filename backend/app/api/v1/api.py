from fastapi import APIRouter
from app.api.v1.endpoints import orders, products, sync, auth

api_router = APIRouter()

api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

