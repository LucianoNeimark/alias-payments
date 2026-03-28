"""Ledger entry schemas."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LedgerEntryType(StrEnum):
    FUNDING_CREDIT = "funding_credit"
    RESERVE = "reserve"
    RELEASE = "release"
    PAYOUT_DEBIT = "payout_debit"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class LedgerDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wallet_id: UUID
    entry_type: str
    direction: str
    amount: Decimal
    currency: str
    reference_type: str
    reference_id: str
    balance_after_available: Decimal
    balance_after_reserved: Decimal
    description: str | None
    created_at: datetime


class LedgerCreateInternal(BaseModel):
    """Payload for creating a ledger row + updating wallet balances (service use)."""

    wallet_id: UUID
    entry_type: LedgerEntryType
    amount: Decimal = Field(..., gt=0)
    currency: str = "ARS"
    reference_type: str = Field(..., min_length=1)
    reference_id: str = Field(..., min_length=1)
    description: str | None = None
    direction: LedgerDirection | None = None
