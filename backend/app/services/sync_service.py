from sqlalchemy.orm import Session
from app.models.sync_log import SyncLog, SyncStatus
from app.services.integrations.etsy_service import EtsyService
from app.services.integrations.tiktok_shop_service import TikTokShopService


class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.etsy_service = EtsyService()
        self.tiktok_shop_service = TikTokShopService()

    async def import_orders(self, sync_log_id: int, source: str):
        """Import orders from the specified source"""
        sync_log = self.db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
        if not sync_log:
            return

        sync_log.status = SyncStatus.IN_PROGRESS
        self.db.commit()

        try:
            if source == "etsy":
                orders = await self.etsy_service.fetch_orders()
            elif source == "tiktok_shop":
                orders = await self.tiktok_shop_service.fetch_orders()
            else:
                raise ValueError(f"Unknown source: {source}")

            # Process and save orders
            # TODO: Implement order processing logic
            sync_log.records_processed = len(orders)
            sync_log.records_successful = len(orders)
            sync_log.status = SyncStatus.SUCCESS

        except Exception as e:
            sync_log.status = SyncStatus.FAILED
            sync_log.error_message = str(e)
            sync_log.records_failed = sync_log.records_processed

        finally:
            from datetime import datetime
            sync_log.completed_at = datetime.utcnow()
            self.db.commit()

    async def export_products(self, sync_log_id: int, source: str):
        """Export products to the specified source"""
        sync_log = self.db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
        if not sync_log:
            return

        sync_log.status = SyncStatus.IN_PROGRESS
        self.db.commit()

        try:
            # TODO: Fetch products from database and export them
            # This will be implemented when product export is needed
            sync_log.status = SyncStatus.SUCCESS
            sync_log.records_processed = 0
            sync_log.records_successful = 0

        except Exception as e:
            sync_log.status = SyncStatus.FAILED
            sync_log.error_message = str(e)

        finally:
            from datetime import datetime
            sync_log.completed_at = datetime.utcnow()
            self.db.commit()

