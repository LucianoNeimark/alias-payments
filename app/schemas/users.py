"""User-related API schemas."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.wallets import WalletResponse


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserCreate(BaseModel):
    auth_provider_user_id: str = Field(..., min_length=1)
    email: EmailStr
    username: str = Field(..., min_length=1)


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    auth_provider_user_id: str
    email: EmailStr
    username: str
    status: str
    created_at: datetime
    updated_at: datetime


class UserWithWalletResponse(BaseModel):
    user: UserResponse
    wallet: WalletResponse
