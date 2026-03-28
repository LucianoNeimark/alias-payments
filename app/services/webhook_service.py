"""Talo webhook processing (idempotent funding reconciliation)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import funding_event_repository, funding_order_repository
from app.schemas.funding import FundingEventResponse, FundingOrderStatus, TaloWebhookPayload
from app.schemas.ledger import LedgerCreateInternal, LedgerEntryType
from app.services import ledger_service, talo_client

logger = logging.getLogger(__name__)

_TALO_STATUS_MAP: dict[str, FundingOrderStatus] = {
    "SUCCESS": FundingOrderStatus.CREDITED,
    "OVERPAID": FundingOrderStatus.OVERPAID,
    "UNDERPAID": FundingOrderStatus.UNDERPAID,
    "EXPIRED": FundingOrderStatus.EXPIRED,
}


def _decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _event_response(row: dict) -> FundingEventResponse:
    return FundingEventResponse.model_validate(row)


async def process_talo_webhook(
    client: Client, payload: TaloWebhookPayload
) -> FundingEventResponse:
    existing = funding_event_repository.get_event_by_provider_event_id(
        client, payload.paymentId
    )
    if existing:
        return _event_response(existing)

    order = funding_order_repository.get_order_by_provider_payment_id(
        client, payload.paymentId
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding order not found for this paymentId",
        )

    order_id = str(order["id"])

    if order.get("status") != FundingOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Funding order is not pending; cannot apply webhook",
        )

    talo_payment = await talo_client.get_payment(payload.paymentId)
    talo_status = talo_payment.get("payment_status", "PENDING")

    if talo_status == "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment is still pending at Talo; nothing to reconcile",
        )

    new_status = _TALO_STATUS_MAP.get(talo_status)
    if new_status is None:
        logger.warning("talo webhook: unmapped status %s for order %s", talo_status, order_id)
        new_status = FundingOrderStatus.FAILED

    total_paid = talo_payment.get("transaction_fields", {}).get("total_paid", {})
    received = _decimal(total_paid.get("amount", 0))

    if received == Decimal("0"):
        transactions = talo_payment.get("user_info", {}).get("transactions", [])
        if transactions:
            received = _decimal(transactions[0].get("amount", 0))

    should_credit = new_status in (
        FundingOrderStatus.CREDITED,
        FundingOrderStatus.OVERPAID,
    ) and received > 0

    now_iso = datetime.now(UTC).isoformat()

    event_data: dict = {
        "funding_order_id": order_id,
        "provider_event_id": payload.paymentId,
        "provider_status": talo_status,
        "received_amount": float(received),
        "raw_payload": talo_payment,
        "processed_at": now_iso,
    }

    event_row = funding_event_repository.create_event(client, event_data)

    try:
        if should_credit:
            ledger_service.record_entry(
                client,
                LedgerCreateInternal(
                    wallet_id=UUID(str(order["wallet_id"])),
                    entry_type=LedgerEntryType.FUNDING_CREDIT,
                    amount=received,
                    currency=str(order.get("currency") or "ARS"),
                    reference_type="funding_order",
                    reference_id=order_id,
                    description="Acreditación de fondeo Talo (webhook)",
                ),
            )

        updated = funding_order_repository.update_order_status(
            client, order_id, new_status.value
        )
        if not updated:
            raise RuntimeError("Funding order status update returned no row")
    except Exception as exc:
        try:
            client.table("funding_events").delete().eq("id", event_row["id"]).execute()
        except Exception:
            pass
        if isinstance(exc, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        raise

    refreshed = funding_event_repository.get_event_by_provider_event_id(
        client, payload.paymentId
    )
    assert refreshed is not None
    return _event_response(refreshed)
