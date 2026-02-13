"""Pydantic Schemas - Users and Authentication."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from ..models.enums import Role


# --- User Schemas (Base) ---

class UserBase(BaseModel):
    phone: str
    email: Optional[str] = None
    first_name: str
    last_name: str


class UserResponse(UserBase):
    id: UUID
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserMeResponse(UserResponse):
    """Extended user info for current user."""
    pass


# --- Auth Schemas ---

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)


class OTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)


class OTPVerify(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    code: str = Field(..., min_length=4, max_length=6)


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    code: Optional[str] = Field(None, min_length=4, max_length=6)


class RegisterResponse(BaseModel):
    message: str
    is_new: bool = True
    user: Optional[UserResponse] = None
    tokens: Optional[Token] = None


# --- User Management Schemas ---

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Role = Role.CLIENT


class UserCreateStaff(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Role = Field(..., description="Staff role: operator, manager, admin")


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: Role


class UserStatusUpdate(BaseModel):
    is_active: bool
