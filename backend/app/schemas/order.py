from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.order import OrderSource, OrderStatus


class OrderBase(BaseModel):
    external_id: str
    source: OrderSource
    status: OrderStatus = OrderStatus.PENDING
    customer_name: str
    customer_email: Optional[EmailStr] = None
    shipping_address: Optional[Dict[str, Any]] = None
    total_amount: float
    currency: str = "USD"
    items: Optional[List[Dict[str, Any]]] = None
    order_date: datetime


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    shipping_address: Optional[Dict[str, Any]] = None
    total_amount: Optional[float] = None
    items: Optional[List[Dict[str, Any]]] = None


class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

