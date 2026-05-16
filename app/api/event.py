"""Order event API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import database_model
from app.schemas.event_schema import OrderEventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/orders/{order_id}", response_model=list[OrderEventResponse])
def get_order_events(order_id: int, db: Session = Depends(get_db)):
    """Return all stored events for one order."""
    return db.query(database_model.OrderEvent).filter(database_model.OrderEvent.order_id == order_id).all()
