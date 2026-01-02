from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.sync_log import SyncType, SyncStatus


class SyncRequest(BaseModel):
    source: str  # "etsy" or "tiktok_shop"


class SyncLog(BaseModel):
    id: int
    sync_type: SyncType
    status: SyncStatus
    source: str
    order_id: Optional[int] = None
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

