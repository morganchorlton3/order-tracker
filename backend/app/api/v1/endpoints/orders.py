from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_session
from app.core.user import get_current_user_id
from app.models.order import Order, OrderSource, OrderStatus
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate
from supertokens_python.recipe.session import SessionContainer

router = APIRouter()


@router.get("/", response_model=List[OrderSchema])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    source: Optional[OrderSource] = None,
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get all orders for the authenticated user with optional filtering"""
    user_id = get_current_user_id(db, session)
    
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if source:
        query = query.filter(Order.source == source)
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/count", response_model=dict)
def get_orders_count(db: Session = Depends(get_db)):
    """Get the total number of orders"""
    return { "count": db.query(Order).count() }


@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get a specific order by ID (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderSchema, status_code=201)
def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Create a new order for the authenticated user"""
    user_id = get_current_user_id(db, session)
    
    order_data = order.dict()
    order_data["user_id"] = user_id
    db_order = Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int, 
    order_update: OrderUpdate, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Update an existing order (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    db_order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Delete an order (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    db_order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return None

