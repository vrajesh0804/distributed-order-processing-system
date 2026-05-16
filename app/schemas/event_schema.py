"""Pydantic schemas for order event responses."""

from datetime import datetime
from pydantic import BaseModel


class OrderEventResponse(BaseModel):
    id: int
    order_id: int
    event_type: str
    payload: str
    created_at: datetime

    model_config = {"from_attributes": True}
