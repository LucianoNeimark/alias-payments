"""PaymentRequest ORM model."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class PaymentRequestStatus(enum.Enum):
    requested = "requested"
    rejected = "rejected"
    insufficient_funds = "insufficient_funds"
    reserved = "reserved"
    executing = "executing"
    completed = "completed"
    failed = "failed"
    needs_manual_review = "needs_manual_review"


class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    __table_args__ = (
        Index("ix_payment_requests_user_id", "user_id"),
        Index("ix_payment_requests_agent_id", "agent_id"),
        Index("ix_payment_requests_wallet_id", "wallet_id"),
        Index("ix_payment_requests_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'ARS'"))
    destination_cvu: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_alias: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_holder_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PaymentRequestStatus] = mapped_column(
        Enum(PaymentRequestStatus, name="payment_request_status", create_type=False),
        nullable=False,
        server_default=text("'requested'"),
    )
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
