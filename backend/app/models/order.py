from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class OrderSource(str, enum.Enum):
    ETSY = "etsy"
    TIKTOK_SHOP = "tiktok_shop"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    source = Column(Enum(OrderSource), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Customer information
    customer_name = Column(String, nullable=False)
    customer_email = Column(String)
    shipping_address = Column(JSON)
    
    # Order details
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    items = Column(JSON)  # List of items with product references
    
    # Timestamps
    order_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    sync_logs = relationship("SyncLog", back_populates="order")

