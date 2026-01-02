from sqlalchemy.orm import Session
from app.models.sync_log import SyncLog, SyncStatus
from app.models.order import Order, OrderSource
from app.services.integrations.etsy_service import EtsyService
from app.services.integrations.tiktok_shop_service import TikTokShopService


class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.etsy_service = EtsyService(db=db)
        self.tiktok_shop_service = TikTokShopService()

    async def import_orders(self, sync_log_id: int, source: str):
        """Import orders from the specified source"""
        from datetime import datetime
        
        # Start with a fresh query to get the sync_log
        sync_log = self.db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
        if not sync_log:
            return

        # Update status to IN_PROGRESS
        sync_log.status = SyncStatus.IN_PROGRESS
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            return

        # Track stats outside of the sync_log object to avoid transaction issues
        records_processed = 0
        records_successful = 0
        records_failed = 0
        error_message = None

        try:
            if source == "etsy":
                receipts = await self.etsy_service.fetch_orders()
                
                # Transform and save orders
                for receipt in receipts:
                    try:
                        # Transform Etsy receipt to our order format
                        order_data = self.etsy_service.transform_receipt_to_order(receipt)
                        
                        # Check if order already exists
                        existing_order = self.db.query(Order).filter(
                            Order.external_id == order_data["external_id"],
                            Order.source == OrderSource.ETSY
                        ).first()
                        
                        if existing_order:
                            # Update existing order
                            for key, value in order_data.items():
                                if key != "external_id" and key != "source":
                                    setattr(existing_order, key, value)
                            records_successful += 1
                        else:
                            # Create new order
                            new_order = Order(**order_data)
                            self.db.add(new_order)
                            records_successful += 1
                        
                        records_processed += 1
                    
                    except Exception as e:
                        records_failed += 1
                        records_processed += 1
                        print(f"Error processing order {receipt.get('receipt_id')}: {e}")
                
                # Commit all the orders
                self.db.commit()
                
            elif source == "tiktok_shop":
                orders = await self.tiktok_shop_service.fetch_orders()
                # TODO: Implement TikTok Shop order processing
                records_processed = len(orders)
                records_successful = len(orders)
            else:
                raise ValueError(f"Unknown source: {source}")

        except Exception as e:
            # Rollback any failed transaction
            self.db.rollback()
            error_message = str(e)
            # If we haven't processed anything, mark as failed
            if records_processed == 0:
                records_failed = 1

        # Update sync_log in a fresh transaction
        try:
            # Re-query to get a fresh object
            sync_log = self.db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
            if sync_log:
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                
                if error_message:
                    sync_log.status = SyncStatus.FAILED
                    sync_log.error_message = error_message
                else:
                    sync_log.status = SyncStatus.SUCCESS
                
                self.db.commit()
        except Exception as e:
            # Last resort - rollback and try one more time
            self.db.rollback()
            try:
                sync_log = self.db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
                if sync_log:
                    sync_log.status = SyncStatus.FAILED
                    sync_log.error_message = error_message or str(e)
                    sync_log.completed_at = datetime.utcnow()
                    self.db.commit()
            except Exception:
                # If we can't even update the sync_log, just rollback
                self.db.rollback()

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

