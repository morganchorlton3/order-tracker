from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_session
from app.core.user import get_current_user_id
from app.models.sync_log import SyncLog, SyncType, SyncStatus
from app.schemas.sync import SyncLog as SyncLogSchema, SyncRequest
from app.services.sync_service import SyncService
from supertokens_python.recipe.session import SessionContainer

router = APIRouter()


@router.post("/orders/import", response_model=SyncLogSchema)
async def sync_orders_import(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Import orders from Etsy or TikTok Shop for the authenticated user"""
    user_id = get_current_user_id(db, session)
    sync_service = SyncService(db, user_id=user_id)
    
    # Create sync log
    sync_log = SyncLog(
        sync_type=SyncType.ORDER_IMPORT,
        status=SyncStatus.PENDING,
        source=sync_request.source
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)
    
    # Run sync in background
    background_tasks.add_task(
        sync_service.import_orders,
        sync_log.id,
        sync_request.source
    )
    
    return sync_log


@router.post("/products/export", response_model=SyncLogSchema)
async def sync_products_export(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Export products to Etsy or TikTok Shop for the authenticated user"""
    user_id = get_current_user_id(db, session)
    sync_service = SyncService(db, user_id=user_id)
    
    # Create sync log
    sync_log = SyncLog(
        sync_type=SyncType.PRODUCT_EXPORT,
        status=SyncStatus.PENDING,
        source=sync_request.source
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)
    
    # Run sync in background
    background_tasks.add_task(
        sync_service.export_products,
        sync_log.id,
        sync_request.source
    )
    
    return sync_log


@router.get("/logs", response_model=List[SyncLogSchema])
def get_sync_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get sync logs"""
    logs = db.query(SyncLog).order_by(SyncLog.started_at.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=SyncLogSchema)
def get_sync_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific sync log"""
    log = db.query(SyncLog).filter(SyncLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sync log not found")
    return log

