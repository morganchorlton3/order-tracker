from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_session
from app.core.user import get_current_user_id
from app.models.order import Order, OrderSource, OrderStatus
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, OrdersResponse
from supertokens_python.recipe.session import SessionContainer

router = APIRouter()


@router.get("/", response_model=OrdersResponse)
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[OrderSource] = None,
    status: Optional[OrderStatus] = None,
    search: Optional[str] = Query(None, description="Search in customer name, email, or external_id"),
    currency: Optional[str] = Query(None, description="Filter by currency code"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum order amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum order amount"),
    date_from: Optional[str] = Query(None, description="Filter orders from this date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter orders to this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get all orders for the authenticated user with optional filtering, pagination, and search"""
    from sqlalchemy import or_, and_
    from datetime import datetime
    
    user_id = get_current_user_id(db, session)
    
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if source:
        query = query.filter(Order.source == source)
    if status:
        query = query.filter(Order.status == status)
    
    # Add search functionality
    if search:
        search_filter = or_(
            Order.customer_name.ilike(f"%{search}%"),
            Order.customer_email.ilike(f"%{search}%"),
            Order.external_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Currency filter
    if currency:
        query = query.filter(Order.currency == currency.upper())
    
    # Amount range filters
    if min_amount is not None:
        query = query.filter(Order.total_amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Order.total_amount <= max_amount)
    
    # Date range filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Order.order_date >= date_from_obj)
        except ValueError:
            pass  # Invalid date format, ignore
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            # Include the entire day by setting time to end of day
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Order.order_date <= date_to_obj)
        except ValueError:
            pass  # Invalid date format, ignore
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination - order by newest first (order_date descending, then id descending as tiebreaker)
    orders = query.order_by(Order.order_date.desc(), Order.id.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": orders,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/count", response_model=dict)
def get_orders_count(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get the total number of orders for the authenticated user"""
    user_id = get_current_user_id(db, session)
    count = db.query(Order).filter(Order.user_id == user_id).count()
    return { "count": count }


@router.get("/stats/last-30-days", response_model=dict)
def get_last_30_days_stats(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get statistics for the last 30 days"""
    from datetime import datetime, timedelta, timezone
    
    user_id = get_current_user_id(db, session)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Get orders from last 30 days
    orders = db.query(Order).filter(
        Order.user_id == user_id,
        Order.order_date >= thirty_days_ago
    ).all()
    
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Count by status
    status_counts = {}
    for order in orders:
        status_counts[order.status.value] = status_counts.get(order.status.value, 0) + 1
    
    # Count by source
    source_counts = {}
    for order in orders:
        source_counts[order.source.value] = source_counts.get(order.source.value, 0) + 1
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_order_value": avg_order_value,
        "status_breakdown": status_counts,
        "source_breakdown": source_counts,
    }


@router.get("/stats/over-time", response_model=dict)
def get_orders_over_time(
    months: int = Query(12, ge=1, le=24, description="Number of months to look back"),
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get order statistics over time grouped by month and channel"""
    from datetime import datetime, timedelta, timezone, date
    from collections import defaultdict
    
    user_id = get_current_user_id(db, session)
    # Calculate start date based on months
    start_date = datetime.now(timezone.utc) - timedelta(days=months * 30)
    
    # Get all orders in the date range
    orders = db.query(Order).filter(
        Order.user_id == user_id,
        Order.order_date >= start_date
    ).all()
    
    # Organize data by month and source
    data_by_month = defaultdict(lambda: {'etsy': {'orders': 0, 'revenue': 0}, 'tiktok_shop': {'orders': 0, 'revenue': 0}})
    
    for order in orders:
        # Extract date part (without time)
        order_date = order.order_date.date() if hasattr(order.order_date, 'date') else order.order_date
        if isinstance(order_date, str):
            order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00')).date()
        elif not isinstance(order_date, date):
            order_date = datetime.fromtimestamp(order_date).date() if isinstance(order_date, (int, float)) else date.today()
        
        # Create month key (YYYY-MM format)
        month_key = f"{order_date.year}-{order_date.month:02d}"
        source = order.source.value
        
        data_by_month[month_key][source]['orders'] += 1
        data_by_month[month_key][source]['revenue'] += order.total_amount
    
    # Convert to list format for frontend, sorted by month
    chart_data = []
    for month_key in sorted(data_by_month.keys()):
        # Format month for display (e.g., "2024-01" -> "Jan 2024")
        year, month = month_key.split('-')
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_display = f"{month_names[int(month) - 1]} {year}"
        
        chart_data.append({
            'month': month_key,
            'month_display': month_display,
            'etsy_orders': data_by_month[month_key]['etsy']['orders'],
            'etsy_revenue': data_by_month[month_key]['etsy']['revenue'],
            'tiktok_shop_orders': data_by_month[month_key]['tiktok_shop']['orders'],
            'tiktok_shop_revenue': data_by_month[month_key]['tiktok_shop']['revenue'],
        })
    
    return {
        "months": months,
        "data": chart_data
    }


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

