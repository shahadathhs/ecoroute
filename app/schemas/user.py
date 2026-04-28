"""
User Management Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import DataResponse


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="User password")
    role: UserRole = Field(default=UserRole.STANDARD_DISPATCHER, description="User role")
    organization_id: str | None = Field(None, description="Organization ID")


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: str | None = Field(None, min_length=1, max_length=255, description="User full name")
    role: UserRole | None = Field(None, description="User role")
    is_active: bool | None = Field(None, description="User active status")


class UserData(BaseModel):
    """User data schema."""

    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    organization_id: str | None = Field(None, description="Organization ID")
    is_active: bool = Field(..., description="User active status")
    last_login: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserInvite(BaseModel):
    """User invitation schema."""

    email: EmailStr = Field(..., description="Invited user email address")
    role: UserRole = Field(..., description="User role")


class RoleUpdateRequest(BaseModel):
    """Role update request schema."""

    role: UserRole = Field(..., description="New user role")


# Response types
UserResponse = DataResponse[UserData]
