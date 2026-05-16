"""
Pydantic schemas for Product APIs.

Schemas define the shape of incoming request data and outgoing response data.
"""

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Data required from client when creating a product. ID is not needed."""

    name: str = Field(..., examples=["Laptop"])
    price: float = Field(..., examples=[1510])
    stock_quantity: int = Field(..., examples=[10])


class ProductUpdate(BaseModel):
    """Data required from client when updating a product."""

    name: str
    price: float
    stock_quantity: int


class ProductResponse(BaseModel):
    """Data returned by API after reading/creating/updating a product."""

    id: int
    name: str
    price: float
    stock_quantity: int

    model_config = {"from_attributes": True}
