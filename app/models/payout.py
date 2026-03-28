"""Payout ORM model."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class PayoutStatus(enum.Enum):
    queued = "queued"
    executing = "executing"
    completed = "completed"
    failed = "failed"
    needs_manual_review = "needs_manual_review"


class Payout(Base):
    __tablename__ = "payouts"
    __table_args__ = (
        Index("ix_payouts_payment_request_id", "payment_request_id"),
        Index("ix_payouts_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    payment_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    execution_provider: Mapped[str] = mapped_column(Text, nullable=False)
    source_account_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_cvu: Mapped[str] = mapped_column(Text, nullable=False)
    destination_alias: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'ARS'"))
    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus, name="payout_status", create_type=False),
        nullable=False,
        server_default=text("'queued'"),
    )
    executor_run_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_receipt_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
