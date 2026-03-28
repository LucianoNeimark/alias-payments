"""Approval records (human decision on a payment request)."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_request_id: UUID
    user_id: UUID
    decision: str
    decision_reason: str | None
    approved_amount: Decimal
    created_at: datetime


class ApprovalCreateInternal(BaseModel):
    """Repository insert payload."""

    payment_request_id: UUID
    user_id: UUID
    decision: ApprovalDecision
    decision_reason: str | None = None
    approved_amount: Decimal = Field(..., ge=0)
