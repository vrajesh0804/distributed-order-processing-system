"""Order API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import database_model
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatusResponse
from app.services.cache_service import get_cached_order_status
from app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_new_order(order_request: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order and publish order_created event to Kafka.

    The API returns quickly with PENDING status. Worker service processes the
    order asynchronously in the background.
    """
    user = db.query(database_model.User).filter(database_model.User.id == order_request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Create user first.")

    try:
        return create_order(db, order_request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(exc)}") from exc


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    """Return full order details by ID."""
    order = db.query(database_model.Order).filter(database_model.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/status", response_model=OrderStatusResponse)
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    """
    Return lightweight order status.

    First checks Redis cache. If cache is missing, it reads from PostgreSQL.
    """
    cached_status = get_cached_order_status(order_id)
    if cached_status:
        return cached_status

    order = db.query(database_model.Order).filter(database_model.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "inventory_status": order.inventory_status,
        "message": "Status loaded from database",
    }
