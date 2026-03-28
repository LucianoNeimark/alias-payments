"""Payout (bank execution) API schemas."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PayoutStatus(StrEnum):
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"


class PayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_request_id: UUID
    execution_provider: str
    source_account_label: str | None
    destination_cvu: str
    destination_alias: str | None
    amount: Decimal
    currency: str
    status: str
    executor_run_id: str | None
    provider_receipt_ref: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class PayoutCreateInternal(BaseModel):
    payment_request_id: UUID
    execution_provider: str = "selenium_mercadopago"
    source_account_label: str = "mp_pool_demo"
    destination_cvu: str = Field(..., min_length=1)
    destination_alias: str | None = None
    amount: Decimal = Field(..., gt=0)
    currency: str = "ARS"
