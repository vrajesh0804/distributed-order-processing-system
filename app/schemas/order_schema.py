"""Pydantic schemas for Order APIs."""

from datetime import datetime
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    """Single item inside an order creation request."""

    product_id: int = Field(..., examples=[1])
    quantity: int = Field(..., gt=0, examples=[2])


class OrderCreate(BaseModel):
    """Request body for creating an order."""

    user_id: int = Field(..., examples=[1])
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    """Response shape for each order item."""

    id: int
    product_id: int
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Full order response."""

    id: int
    user_id: int
    status: str
    total_amount: float
    payment_status: str
    inventory_status: str
    created_at: datetime
    updated_at: datetime | None = None
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderStatusResponse(BaseModel):
    """Lightweight response for checking order processing status."""

    order_id: int
    status: str
    payment_status: str
    inventory_status: str
    message: str
