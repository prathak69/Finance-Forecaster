from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters",
    )
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
