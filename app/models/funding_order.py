"""FundingOrder ORM model."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Index, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class FundingOrderStatus(enum.Enum):
    pending = "pending"
    credited = "credited"
    underpaid = "underpaid"
    overpaid = "overpaid"
    expired = "expired"
    failed = "failed"


class FundingOrder(Base):
    __tablename__ = "funding_orders"
    __table_args__ = (
        Index("ix_funding_orders_user_id", "user_id"),
        Index("ix_funding_orders_wallet_id", "wallet_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    requested_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'ARS'"))
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    provider_payment_id: Mapped[str] = mapped_column(Text, nullable=False)
    cvu: Mapped[str] = mapped_column(Text, nullable=False)
    alias: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[FundingOrderStatus] = mapped_column(
        Enum(FundingOrderStatus, name="funding_order_status", create_type=False),
        nullable=False,
        server_default=text("'pending'"),
    )
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
