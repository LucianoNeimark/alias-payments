"""Agent-related API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    user_id: UUID
    name: str = Field(..., min_length=1)
    description: str | None = None
    default_spending_limit: Decimal | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    default_spending_limit: Decimal | None = None
    is_active: bool | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    default_spending_limit: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
