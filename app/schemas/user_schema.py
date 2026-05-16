"""Pydantic schemas for basic user APIs."""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request body for creating a user."""

    name: str = Field(..., examples=["Test"])
    email: EmailStr = Field(..., examples=["test@example.com"])
    password: str = Field(..., examples=["password"])


class UserResponse(BaseModel):
    """Response body for user APIs. Password is intentionally not returned."""

    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}
