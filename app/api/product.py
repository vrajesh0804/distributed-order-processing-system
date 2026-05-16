"""
Product API routes.

APIRouter lets us keep product endpoints in a separate file instead of putting
everything inside main.py.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import database_model
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product in PostgreSQL."""
    new_product = database_model.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/", response_model=list[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Return all products from database."""
    return db.query(database_model.Product).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Return one product by ID."""
    product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Update product details."""
    existing_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.stock_quantity = product.stock_quantity
    db.commit()
    db.refresh(existing_product)
    return existing_product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete product by ID."""
    product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
