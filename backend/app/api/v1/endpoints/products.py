from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_session
from app.core.user import get_current_user_id
from app.models.product import Product, ProductStatus
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate
from supertokens_python.recipe.session import SessionContainer

router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[ProductStatus] = None,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get all products for the authenticated user with optional filtering"""
    user_id = get_current_user_id(db, session)
    
    query = db.query(Product).filter(Product.user_id == user_id)
    
    if status:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductSchema)
def get_product(
    product_id: int, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get a specific product by ID (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Create a new product for the authenticated user"""
    user_id = get_current_user_id(db, session)
    
    product_data = product.dict()
    product_data["user_id"] = user_id
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Update an existing product (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Delete a product (only if it belongs to the authenticated user)"""
    user_id = get_current_user_id(db, session)
    
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None

