from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., max_length=64)


class UserResponse(BaseModel):
    """Schema for user data in responses (without password)."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
