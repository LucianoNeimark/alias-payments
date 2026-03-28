"""Wallet API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    currency: str
    available_balance: Decimal
    reserved_balance: Decimal
    created_at: datetime
    updated_at: datetime
