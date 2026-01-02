from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.product import ProductStatus


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    price: float
    currency: str = "USD"
    quantity: int = 0
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    variants: Optional[Dict[str, Any]] = None
    status: ProductStatus = ProductStatus.DRAFT
    etsy_listing_id: Optional[str] = None
    tiktok_shop_product_id: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    quantity: Optional[int] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    variants: Optional[Dict[str, Any]] = None
    status: Optional[ProductStatus] = None
    etsy_listing_id: Optional[str] = None
    tiktok_shop_product_id: Optional[str] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

