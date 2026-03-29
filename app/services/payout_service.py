"""Payout execution orchestration (ledger finalize / release)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import payment_request_repository, payout_repository
from app.schemas.ledger import LedgerCreateInternal, LedgerEntryType
from app.schemas.payment_requests import PaymentRequestStatus
from app.schemas.payouts import PayoutResponse, PayoutStatus
from app.services import bank_executor
from app.services import ledger_service


def _decimal(val) -> Decimal:
    if val is None:
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _payout_response(row: dict) -> PayoutResponse:
    return PayoutResponse.model_validate(row)


async def execute_payout(
    client: Client,
    payout_id: str,
    *,
    force_failure: bool = False,
    force_manual_review: bool = False,
    timeout_seconds: float = 60.0,
) -> PayoutResponse:
    payout = payout_repository.get_by_id(client, payout_id)
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found",
        )

    if payout.get("status") != PayoutStatus.QUEUED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only queued payouts can be executed",
        )

    pr_id = str(payout["payment_request_id"])
    pr = payment_request_repository.get_by_id(client, pr_id)
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found for payout",
        )

    if pr.get("status") != PaymentRequestStatus.RESERVED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment request must be in reserved state to execute payout",
        )

    wallet_id = UUID(str(pr["wallet_id"]))
    amount = _decimal(payout.get("amount"))

    payment_request_repository.update_payment_request(
        client, pr_id, {"status": PaymentRequestStatus.EXECUTING.value}
    )
    payout_repository.update_payout(
        client, payout_id, {"status": PayoutStatus.EXECUTING.value}
    )

    result = await bank_executor.run_transfer(
        amount=amount,
        destination_cvu=str(payout["destination_cvu"]),
        destination_alias=payout.get("destination_alias"),
        timeout_seconds=timeout_seconds,
        force_failure=force_failure,
        force_manual_review=force_manual_review,
    )

    if result.success:
        try:
            ledger_service.record_entry(
                client,
                LedgerCreateInternal(
                    wallet_id=wallet_id,
                    entry_type=LedgerEntryType.PAYOUT_DEBIT,
                    amount=amount,
                    currency=str(payout.get("currency") or "ARS"),
                    reference_type="payout",
                    reference_id=payout_id,
                    description="Débito por pago ejecutado (pool MP)",
                ),
            )
        except Exception as exc:
            payout_repository.update_payout(
                client,
                payout_id,
                {
                    "status": PayoutStatus.NEEDS_MANUAL_REVIEW.value,
                    "executor_run_id": result.executor_run_id,
                    "failure_reason": f"Ledger error after bank success: {exc}",
                },
            )
            payment_request_repository.update_payment_request(
                client,
                pr_id,
                {"status": PaymentRequestStatus.NEEDS_MANUAL_REVIEW.value},
            )
            refreshed = payout_repository.get_by_id(client, payout_id)
            assert refreshed is not None
            return _payout_response(refreshed)

        payout_repository.update_payout(
            client,
            payout_id,
            {
                "status": PayoutStatus.COMPLETED.value,
                "executor_run_id": result.executor_run_id,
                "provider_receipt_ref": result.provider_receipt_ref,
                "failure_reason": None,
            },
        )
        payment_request_repository.update_payment_request(
            client, pr_id, {"status": PaymentRequestStatus.COMPLETED.value}
        )
    else:
        if result.needs_manual_review:
            payout_repository.update_payout(
                client,
                payout_id,
                {
                    "status": PayoutStatus.NEEDS_MANUAL_REVIEW.value,
                    "executor_run_id": result.executor_run_id,
                    "failure_reason": result.failure_reason,
                },
            )
            payment_request_repository.update_payment_request(
                client,
                pr_id,
                {"status": PaymentRequestStatus.NEEDS_MANUAL_REVIEW.value},
            )
        else:
            try:
                ledger_service.record_entry(
                    client,
                    LedgerCreateInternal(
                        wallet_id=wallet_id,
                        entry_type=LedgerEntryType.RELEASE,
                        amount=amount,
                        currency=str(payout.get("currency") or "ARS"),
                        reference_type="payout",
                        reference_id=payout_id,
                        description="Liberación por fallo de ejecución bancaria",
                    ),
                )
            except ValueError as exc:
                payout_repository.update_payout(
                    client,
                    payout_id,
                    {
                        "status": PayoutStatus.NEEDS_MANUAL_REVIEW.value,
                        "executor_run_id": result.executor_run_id,
                        "failure_reason": f"Release failed: {exc}",
                    },
                )
                payment_request_repository.update_payment_request(
                    client,
                    pr_id,
                    {"status": PaymentRequestStatus.NEEDS_MANUAL_REVIEW.value},
                )
                refreshed = payout_repository.get_by_id(client, payout_id)
                assert refreshed is not None
                return _payout_response(refreshed)

            payout_repository.update_payout(
                client,
                payout_id,
                {
                    "status": PayoutStatus.FAILED.value,
                    "executor_run_id": result.executor_run_id,
                    "failure_reason": result.failure_reason,
                },
            )
            payment_request_repository.update_payment_request(
                client, pr_id, {"status": PaymentRequestStatus.FAILED.value}
            )

    refreshed = payout_repository.get_by_id(client, payout_id)
    assert refreshed is not None
    return _payout_response(refreshed)


def list_payouts(
    client: Client,
    limit: int = 50,
    offset: int = 0,
    payment_request_id: str | None = None,
) -> list[PayoutResponse]:
    capped = min(max(limit, 1), 100)
    rows = payout_repository.list_payouts(
        client, capped, max(offset, 0), payment_request_id=payment_request_id
    )
    return [_payout_response(r) for r in rows]


async def retry_payout(
    client: Client,
    payout_id: str,
    *,
    force_failure: bool = False,
    force_manual_review: bool = False,
) -> PayoutResponse:
    """Re-queue a needs_manual_review or failed payout and execute it again."""
    payout = payout_repository.get_by_id(client, payout_id)
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found",
        )

    retryable = {PayoutStatus.NEEDS_MANUAL_REVIEW.value, PayoutStatus.FAILED.value}
    if payout.get("status") not in retryable:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only payouts in {retryable} can be retried, current: {payout.get('status')}",
        )

    pr_id = str(payout["payment_request_id"])
    pr = payment_request_repository.get_by_id(client, pr_id)
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment request not found for payout",
        )

    payout_repository.update_payout(
        client, payout_id, {"status": PayoutStatus.QUEUED.value, "failure_reason": None}
    )
    payment_request_repository.update_payment_request(
        client, pr_id, {"status": PaymentRequestStatus.RESERVED.value}
    )

    return await execute_payout(
        client,
        payout_id,
        force_failure=force_failure,
        force_manual_review=force_manual_review,
    )


def get_payout(client: Client, payout_id: str) -> PayoutResponse:
    row = payout_repository.get_by_id(client, payout_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found",
        )
    return _payout_response(row)
