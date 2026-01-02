from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    sku = Column(String, unique=True, index=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Inventory
    quantity = Column(Integer, default=0)
    
    # Product details
    images = Column(JSON)  # List of image URLs
    tags = Column(JSON)  # List of tags
    variants = Column(JSON)  # Product variants (size, color, etc.)
    
    # Status
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT)
    
    # External sync mappings
    etsy_listing_id = Column(String, nullable=True, index=True)
    tiktok_shop_product_id = Column(String, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

