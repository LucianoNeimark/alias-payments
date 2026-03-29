"""Dashboard /me response schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agents import AgentResponse
from app.schemas.funding import FundingOrderResponse
from app.schemas.ledger import LedgerEntryResponse
from app.schemas.payment_requests import PaymentRequestResponse
from app.schemas.payouts import PayoutResponse
from app.schemas.users import UserResponse
from app.schemas.wallets import WalletResponse


class MeStatsResponse(BaseModel):
    """Aggregated counts for dashboard widgets."""

    pending_payment_requests: int
    active_agents: int
    total_agents: int
    wallet_available: Decimal
    wallet_reserved: Decimal
    payouts_completed: int
    payouts_failed: int
    payouts_needs_manual_review: int


class MeResponse(BaseModel):
    """Profile + wallet + snapshot lists for the home dashboard."""

    model_config = ConfigDict(from_attributes=True)

    user: UserResponse
    wallet: WalletResponse | None
    agents: list[AgentResponse]
    pending_payment_requests_count: int
    recent_payment_requests: list[PaymentRequestResponse]
    recent_payouts: list[PayoutResponse]
    recent_ledger_entries: list[LedgerEntryResponse]


class DashboardPaymentApproveBody(BaseModel):
    """Approve body when the user is inferred from the JWT (no user_id)."""

    approved_amount: Decimal | None = Field(
        default=None,
        description="If omitted, full payment request amount is approved.",
    )
    decision_reason: str | None = None


class DashboardPaymentRejectBody(BaseModel):
    decision_reason: str | None = None


class ActivityItem(BaseModel):
    """Unified recent activity row (optional client display helper)."""

    model_config = ConfigDict(from_attributes=True)

    kind: str
    id: UUID
    title: str
    subtitle: str | None
    amount: Decimal | None
    currency: str | None
    status: str | None
    created_at: datetime
