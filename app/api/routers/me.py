"""Dashboard routes scoped to the authenticated Supabase user (JWT)."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.api.dependencies.auth import CurrentUser
from app.database import get_supabase_client
from app.repositories import (
    agent_repository,
    payment_request_repository,
    payout_repository,
    wallet_repository,
)
from app.schemas.approvals import ApprovalResponse
from app.schemas.agents import AgentResponse, AgentUpdate
from app.schemas.funding import FundingOrderResponse
from app.schemas.me import (
    ActivityItem,
    DashboardPaymentApproveBody,
    DashboardPaymentRejectBody,
    MeResponse,
    MeStatsResponse,
)
from app.schemas.payment_requests import (
    PaymentRequestApprove,
    PaymentRequestReject,
    PaymentRequestResponse,
    PaymentRequestStatus,
)
from app.schemas.ledger import LedgerEntryResponse
from app.schemas.payouts import PayoutResponse, PayoutStatus
from app.schemas.users import UserResponse
from app.schemas.wallets import WalletResponse
from app.services import (
    agent_service,
    approval_service,
    funding_service,
    ledger_service,
    payment_request_service,
    payout_service,
)

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


def _internal_user_id(current_user: dict) -> str:
    return str(current_user["id"])


def _require_payment_request_for_user(
    client: Client, payment_request_id: str, user_id: str
) -> None:
    row = payment_request_repository.get_by_id(client, payment_request_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found",
        )
    if str(row.get("user_id")) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this payment request",
        )


def _require_payout_for_user(client: Client, payout_id: str, user_id: str) -> None:
    payout = payout_repository.get_by_id(client, payout_id)
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found",
        )
    pr_id = str(payout["payment_request_id"])
    row = payment_request_repository.get_by_id(client, pr_id)
    if not row or str(row.get("user_id")) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this payout",
        )


def _require_agent_for_user(client: Client, agent_id: str, user_id: str) -> None:
    agent = agent_repository.get_agent_by_id(client, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    if str(agent.get("user_id")) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this agent",
        )


@router.get("", response_model=MeResponse)
def get_me(
    client: SupabaseDep,
    current_user: CurrentUser,
) -> MeResponse:
    uid = _internal_user_id(current_user)
    user = UserResponse.model_validate(current_user)
    wallet_row = wallet_repository.get_wallet_by_user_id(client, uid)
    wallet = WalletResponse.model_validate(wallet_row) if wallet_row else None

    agents = agent_service.list_agents_for_user(client, uid)
    pending = payment_request_repository.count_by_user_id_and_status(
        client, uid, PaymentRequestStatus.REQUESTED.value
    )
    recent_pr = payment_request_service.list_payment_requests_for_user(
        client, uid, limit=5, offset=0
    )
    recent_po = payout_service.list_payouts_for_user(client, uid, limit=5, offset=0)
    ledger_entries: list = []
    if wallet_row:
        ledger_entries = ledger_service.get_entries_for_wallet(
            client, str(wallet_row["id"]), limit=5, offset=0
        )

    return MeResponse(
        user=user,
        wallet=wallet,
        agents=agents,
        pending_payment_requests_count=pending,
        recent_payment_requests=recent_pr,
        recent_payouts=recent_po,
        recent_ledger_entries=ledger_entries,
    )


@router.get("/stats", response_model=MeStatsResponse)
def get_me_stats(
    client: SupabaseDep,
    current_user: CurrentUser,
) -> MeStatsResponse:
    uid = _internal_user_id(current_user)
    wallet_row = wallet_repository.get_wallet_by_user_id(client, uid)
    avail = Decimal(str(wallet_row.get("available_balance", 0))) if wallet_row else Decimal("0")
    resv = Decimal(str(wallet_row.get("reserved_balance", 0))) if wallet_row else Decimal("0")

    pending = payment_request_repository.count_by_user_id_and_status(
        client, uid, PaymentRequestStatus.REQUESTED.value
    )
    active = agent_repository.count_active_agents_for_user(client, uid)
    total = agent_repository.count_agents_for_user(client, uid)

    completed = payout_repository.count_for_user_by_status(
        client, uid, PayoutStatus.COMPLETED.value
    )
    failed = payout_repository.count_for_user_by_status(
        client, uid, PayoutStatus.FAILED.value
    )
    manual = payout_repository.count_for_user_by_status(
        client, uid, PayoutStatus.NEEDS_MANUAL_REVIEW.value
    )

    return MeStatsResponse(
        pending_payment_requests=pending,
        active_agents=active,
        total_agents=total,
        wallet_available=avail,
        wallet_reserved=resv,
        payouts_completed=completed,
        payouts_failed=failed,
        payouts_needs_manual_review=manual,
    )


@router.get("/activity", response_model=list[ActivityItem])
def get_me_activity(
    client: SupabaseDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 15,
) -> list[ActivityItem]:
    """Merge recent payment requests and payouts for an activity feed."""
    uid = _internal_user_id(current_user)
    prs = payment_request_service.list_payment_requests_for_user(
        client, uid, limit=limit, offset=0
    )
    pos = payout_service.list_payouts_for_user(client, uid, limit=limit, offset=0)
    items: list[ActivityItem] = []
    for p in prs:
        items.append(
            ActivityItem(
                kind="payment_request",
                id=p.id,
                title=f"Payment — {p.purpose[:50]}{'…' if len(p.purpose) > 50 else ''}",
                subtitle=p.destination_cvu or p.destination_alias or "",
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                created_at=p.created_at,
            )
        )
    for po in pos:
        items.append(
            ActivityItem(
                kind="payout",
                id=po.id,
                title=f"Payout to {po.destination_cvu}",
                subtitle=po.provider_receipt_ref,
                amount=po.amount,
                currency=po.currency,
                status=po.status,
                created_at=po.created_at,
            )
        )
    items.sort(key=lambda x: x.created_at, reverse=True)
    return items[:limit]


@router.get("/payment-requests", response_model=list[PaymentRequestResponse])
def list_my_payment_requests(
    client: SupabaseDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: Annotated[str | None, Query(description="Filter by payment_request status")] = None,
) -> list[PaymentRequestResponse]:
    uid = _internal_user_id(current_user)
    return payment_request_service.list_payment_requests_for_user(
        client, uid, limit=limit, offset=offset, filter_status=status
    )


@router.get(
    "/payment-requests/{payment_request_id}",
    response_model=PaymentRequestResponse,
)
def get_my_payment_request(
    payment_request_id: str,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> PaymentRequestResponse:
    uid = _internal_user_id(current_user)
    _require_payment_request_for_user(client, payment_request_id, uid)
    return payment_request_service.get_payment_request(client, payment_request_id)


@router.get(
    "/payment-requests/{payment_request_id}/approvals",
    response_model=list[ApprovalResponse],
)
def list_my_payment_request_approvals(
    payment_request_id: str,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> list[ApprovalResponse]:
    uid = _internal_user_id(current_user)
    _require_payment_request_for_user(client, payment_request_id, uid)
    return approval_service.list_approvals_for_payment_request(
        client, payment_request_id
    )


@router.post(
    "/payment-requests/{payment_request_id}/approve",
    response_model=PaymentRequestResponse,
)
def approve_my_payment_request(
    payment_request_id: str,
    body: DashboardPaymentApproveBody,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> PaymentRequestResponse:
    uid = UUID(_internal_user_id(current_user))
    _require_payment_request_for_user(client, payment_request_id, str(uid))
    approve = PaymentRequestApprove(
        user_id=uid,
        approved_amount=body.approved_amount,
        decision_reason=body.decision_reason,
    )
    return payment_request_service.approve_payment_request(
        client, payment_request_id, approve
    )


@router.post(
    "/payment-requests/{payment_request_id}/reject",
    response_model=PaymentRequestResponse,
)
def reject_my_payment_request(
    payment_request_id: str,
    body: DashboardPaymentRejectBody,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> PaymentRequestResponse:
    uid = UUID(_internal_user_id(current_user))
    _require_payment_request_for_user(client, payment_request_id, str(uid))
    reject = PaymentRequestReject(
        user_id=uid,
        decision_reason=body.decision_reason,
    )
    return payment_request_service.reject_payment_request(
        client, payment_request_id, reject
    )


@router.get("/agents", response_model=list[AgentResponse])
def list_my_agents(
    client: SupabaseDep,
    current_user: CurrentUser,
) -> list[AgentResponse]:
    uid = _internal_user_id(current_user)
    return agent_service.list_agents_for_user(client, uid)


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
def patch_my_agent(
    agent_id: str,
    body: AgentUpdate,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> AgentResponse:
    uid = _internal_user_id(current_user)
    _require_agent_for_user(client, agent_id, uid)
    return agent_service.update_agent(client, agent_id, body)


@router.get("/payouts", response_model=list[PayoutResponse])
def list_my_payouts(
    client: SupabaseDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PayoutResponse]:
    uid = _internal_user_id(current_user)
    return payout_service.list_payouts_for_user(client, uid, limit=limit, offset=offset)


@router.post("/payouts/{payout_id}/execute", response_model=PayoutResponse)
async def execute_my_payout(
    payout_id: str,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> PayoutResponse:
    uid = _internal_user_id(current_user)
    _require_payout_for_user(client, payout_id, uid)
    return await payout_service.execute_payout(client, payout_id)


@router.post("/payouts/{payout_id}/retry", response_model=PayoutResponse)
async def retry_my_payout(
    payout_id: str,
    client: SupabaseDep,
    current_user: CurrentUser,
) -> PayoutResponse:
    uid = _internal_user_id(current_user)
    _require_payout_for_user(client, payout_id, uid)
    return await payout_service.retry_payout(client, payout_id)


@router.get("/funding-orders", response_model=list[FundingOrderResponse])
def list_my_funding_orders(
    client: SupabaseDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[FundingOrderResponse]:
    uid = _internal_user_id(current_user)
    return funding_service.list_funding_orders(client, uid, limit=limit, offset=offset)


@router.get("/ledger", response_model=list[LedgerEntryResponse])
def list_my_ledger(
    client: SupabaseDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[LedgerEntryResponse]:
    uid = _internal_user_id(current_user)
    wallet_row = wallet_repository.get_wallet_by_user_id(client, uid)
    if not wallet_row:
        return []
    return ledger_service.get_entries_for_wallet(
        client, str(wallet_row["id"]), limit=limit, offset=offset
    )
