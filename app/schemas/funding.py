"""Funding orders and Talo webhook schemas."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FundingOrderStatus(StrEnum):
    PENDING = "pending"
    CREDITED = "credited"
    UNDERPAID = "underpaid"
    OVERPAID = "overpaid"
    EXPIRED = "expired"
    FAILED = "failed"


class FundingOrderCreate(BaseModel):
    user_id: UUID
    requested_amount: Decimal = Field(..., gt=0)
    currency: str = "ARS"


class FundingOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    wallet_id: UUID
    requested_amount: Decimal
    currency: str
    provider: str
    provider_payment_id: str
    cvu: str
    alias: str | None
    status: str
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FundingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    funding_order_id: UUID
    provider_event_id: str
    provider_status: str
    received_amount: Decimal
    raw_payload: dict[str, Any] | None
    processed_at: datetime | None
    created_at: datetime


class TaloWebhookPayload(BaseModel):
    """Mock Talo webhook body; adjust when integrating real Talo."""

    provider_event_id: str = Field(..., min_length=1)
    funding_order_id: UUID
    status: str = Field(..., min_length=1)
    received_amount: Decimal = Field(..., ge=0)
    raw_payload: dict[str, Any] | None = None
