"""Payment request domain service (state machine, approvals, payout enqueue)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import (
    agent_repository,
    approval_repository,
    payment_request_repository,
    payout_repository,
    user_repository,
    wallet_repository,
)
from app.schemas.approvals import ApprovalDecision
from app.schemas.ledger import LedgerCreateInternal, LedgerEntryType
from app.schemas.payment_requests import (
    PaymentRequestApprove,
    PaymentRequestCreate,
    PaymentRequestReject,
    PaymentRequestResponse,
    PaymentRequestStatus,
)
from app.schemas.payouts import PayoutCreateInternal, PayoutStatus
from app.services import ledger_service


def _decimal(val) -> Decimal:
    if val is None:
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _response(row: dict) -> PaymentRequestResponse:
    return PaymentRequestResponse.model_validate(row)


def _require_agent_for_user(client: Client, agent_id: str, user_id: str) -> dict:
    agent = agent_repository.get_agent_by_id(client, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    if str(agent.get("user_id")) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to this user",
        )
    if not agent.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not active",
        )
    return agent


def _require_wallet_for_user(client: Client, user_id: str) -> dict:
    wallet = wallet_repository.get_wallet_by_user_id(client, user_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for user",
        )
    return wallet


def create_payment_request(
    client: Client, payload: PaymentRequestCreate
) -> PaymentRequestResponse:
    uid = str(payload.user_id)
    if not user_repository.get_user_by_id(client, uid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing = payment_request_repository.get_by_idempotency_key(
        client, payload.idempotency_key
    )
    if existing:
        if str(existing.get("user_id")) != uid:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key already used by another user",
            )
        if (
            str(existing.get("agent_id")) != str(payload.agent_id)
            or _decimal(existing.get("amount")) != payload.amount
            or str(existing.get("destination_cvu")) != payload.destination_cvu
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key reused with different payload",
            )
        return _response(existing)

    _require_agent_for_user(client, str(payload.agent_id), uid)
    wallet = _require_wallet_for_user(client, uid)

    agent_row = agent_repository.get_agent_by_id(client, str(payload.agent_id))
    assert agent_row is not None
    limit = agent_row.get("default_spending_limit")
    if limit is not None and _decimal(limit) < payload.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount exceeds agent default_spending_limit",
        )

    row_data = {
        "user_id": uid,
        "agent_id": str(payload.agent_id),
        "wallet_id": str(wallet["id"]),
        "amount": float(payload.amount),
        "currency": payload.currency,
        "destination_cvu": payload.destination_cvu,
        "destination_alias": payload.destination_alias,
        "destination_holder_name": payload.destination_holder_name,
        "purpose": payload.purpose,
        "status": PaymentRequestStatus.REQUESTED.value,
        "idempotency_key": payload.idempotency_key,
    }

    row = payment_request_repository.create_payment_request(client, row_data)
    return _response(row)


def get_payment_request(client: Client, payment_request_id: str) -> PaymentRequestResponse:
    row = payment_request_repository.get_by_id(client, payment_request_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found",
        )
    return _response(row)


def list_payment_requests_for_user(
    client: Client, user_id: str, limit: int = 50, offset: int = 0
) -> list[PaymentRequestResponse]:
    if not user_repository.get_user_by_id(client, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    capped = min(max(limit, 1), 100)
    rows = payment_request_repository.list_by_user_id(
        client, user_id, capped, max(offset, 0)
    )
    return [_response(r) for r in rows]


def approve_payment_request(
    client: Client, payment_request_id: str, body: PaymentRequestApprove
) -> PaymentRequestResponse:
    row = payment_request_repository.get_by_id(client, payment_request_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found",
        )

    if str(row.get("user_id")) != str(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can approve this payment request",
        )

    st = row.get("status")
    if st not in (
        PaymentRequestStatus.REQUESTED.value,
        PaymentRequestStatus.FAILED.value,
        PaymentRequestStatus.INSUFFICIENT_FUNDS.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve payment request in status {st}",
        )

    amount_req = _decimal(row.get("amount"))
    approved_amt = body.approved_amount if body.approved_amount is not None else amount_req
    if approved_amt <= 0 or approved_amt > amount_req:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="approved_amount must be positive and not greater than request amount",
        )

    wallet_id = UUID(str(row["wallet_id"]))
    order_id = str(row["id"])
    previous_status = str(row.get("status") or PaymentRequestStatus.REQUESTED.value)

    approval_data = {
        "payment_request_id": order_id,
        "user_id": str(body.user_id),
        "decision": ApprovalDecision.APPROVED.value,
        "decision_reason": body.decision_reason,
        "approved_amount": float(approved_amt),
    }
    approval_row = approval_repository.create_approval(client, approval_data)

    try:
        ledger_service.record_entry(
            client,
            LedgerCreateInternal(
                wallet_id=wallet_id,
                entry_type=LedgerEntryType.RESERVE,
                amount=approved_amt,
                currency=str(row.get("currency") or "ARS"),
                reference_type="payment_request",
                reference_id=order_id,
                description="Reserva por aprobación de pago",
            ),
        )
    except ValueError as exc:
        try:
            client.table("approvals").delete().eq("id", approval_row["id"]).execute()
        except Exception:
            pass
        payment_request_repository.update_payment_request(
            client,
            order_id,
            {"status": PaymentRequestStatus.INSUFFICIENT_FUNDS.value},
        )
        refreshed = payment_request_repository.get_by_id(client, order_id)
        assert refreshed is not None
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    payment_request_repository.update_payment_request(
        client,
        order_id,
        {"status": PaymentRequestStatus.RESERVED.value},
    )

    payout_data = PayoutCreateInternal(
        payment_request_id=UUID(order_id),
        destination_cvu=str(row["destination_cvu"]),
        destination_alias=row.get("destination_alias"),
        amount=approved_amt,
        currency=str(row.get("currency") or "ARS"),
    )
    payout_insert = {
        "payment_request_id": order_id,
        "execution_provider": payout_data.execution_provider,
        "source_account_label": payout_data.source_account_label,
        "destination_cvu": payout_data.destination_cvu,
        "destination_alias": payout_data.destination_alias,
        "amount": float(payout_data.amount),
        "currency": payout_data.currency,
        "status": PayoutStatus.QUEUED.value,
    }
    try:
        payout_repository.create_payout(client, payout_insert)
    except Exception as exc:
        try:
            ledger_service.record_entry(
                client,
                LedgerCreateInternal(
                    wallet_id=wallet_id,
                    entry_type=LedgerEntryType.RELEASE,
                    amount=approved_amt,
                    currency=str(row.get("currency") or "ARS"),
                    reference_type="payment_request",
                    reference_id=order_id,
                    description="Rollback: fallo al crear payout tras reserva",
                ),
            )
        except Exception as release_exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Could not create payout and release failed; manual reconciliation "
                    f"required: {release_exc}"
                ),
            ) from release_exc
        try:
            client.table("approvals").delete().eq("id", approval_row["id"]).execute()
        except Exception:
            pass
        payment_request_repository.update_payment_request(
            client, order_id, {"status": previous_status}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create payout: {exc}",
        ) from exc

    refreshed = payment_request_repository.get_by_id(client, order_id)
    assert refreshed is not None
    return _response(refreshed)


def reject_payment_request(
    client: Client, payment_request_id: str, body: PaymentRequestReject
) -> PaymentRequestResponse:
    row = payment_request_repository.get_by_id(client, payment_request_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found",
        )

    if str(row.get("user_id")) != str(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can reject this payment request",
        )

    if row.get("status") != PaymentRequestStatus.REQUESTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only requested payment requests can be rejected",
        )

    order_id = str(row["id"])
    approval_data = {
        "payment_request_id": order_id,
        "user_id": str(body.user_id),
        "decision": ApprovalDecision.REJECTED.value,
        "decision_reason": body.decision_reason,
        "approved_amount": 0.0,
    }
    approval_repository.create_approval(client, approval_data)

    updated = payment_request_repository.update_payment_request(
        client,
        order_id,
        {"status": PaymentRequestStatus.REJECTED.value},
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update payment request",
        )
    return _response(updated)
