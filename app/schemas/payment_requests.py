"""Payment request API schemas."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PaymentRequestStatus(StrEnum):
    REQUESTED = "requested"
    REJECTED = "rejected"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    RESERVED = "reserved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"


class PaymentRequestCreate(BaseModel):
    user_id: UUID
    agent_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = "ARS"
    destination_cvu: str | None = Field(default=None, min_length=1)
    destination_alias: str | None = Field(default=None, min_length=1)
    destination_holder_name: str | None = None
    purpose: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def require_cvu_or_alias(self) -> "PaymentRequestCreate":
        if not self.destination_cvu and not self.destination_alias:
            raise ValueError(
                "Debe proporcionarse al menos uno de destination_cvu o destination_alias."
            )
        return self


class PaymentRequestApprove(BaseModel):
    user_id: UUID
    approved_amount: Decimal | None = Field(
        default=None,
        description="If omitted, full payment request amount is approved.",
    )
    decision_reason: str | None = None


class PaymentRequestReject(BaseModel):
    user_id: UUID
    decision_reason: str | None = None


class PaymentRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    agent_id: UUID
    wallet_id: UUID
    amount: Decimal
    currency: str
    destination_cvu: str | None
    destination_alias: str | None
    destination_holder_name: str | None
    purpose: str
    status: str
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
