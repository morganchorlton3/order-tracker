from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SyncType(str, enum.Enum):
    ORDER_IMPORT = "order_import"
    ORDER_EXPORT = "order_export"
    PRODUCT_IMPORT = "product_import"
    PRODUCT_EXPORT = "product_export"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(Enum(SyncType), nullable=False)
    status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    source = Column(String, nullable=False)  # "etsy" or "tiktok_shop"
    
    # Related order (if applicable)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    order = relationship("Order", back_populates="sync_logs")
    
    # Sync details
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

