"""Talo webhook processing (idempotent funding reconciliation)."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import funding_event_repository, funding_order_repository
from app.schemas.funding import FundingEventResponse, FundingOrderStatus, TaloWebhookPayload
from app.schemas.ledger import LedgerCreateInternal, LedgerEntryType
from app.services import ledger_service


def _decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _event_response(row: dict) -> FundingEventResponse:
    return FundingEventResponse.model_validate(row)


def process_talo_webhook(
    client: Client, payload: TaloWebhookPayload
) -> FundingEventResponse:
    existing = funding_event_repository.get_event_by_provider_event_id(
        client, payload.provider_event_id
    )
    if existing:
        return _event_response(existing)

    order_id = str(payload.funding_order_id)
    order = funding_order_repository.get_order_by_id(client, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding order not found",
        )

    if order.get("status") != FundingOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Funding order is not pending; cannot apply webhook",
        )

    requested = _decimal(order.get("requested_amount"))
    received = payload.received_amount

    if received == requested:
        new_status = FundingOrderStatus.CREDITED
    elif received < requested:
        new_status = FundingOrderStatus.UNDERPAID
    else:
        new_status = FundingOrderStatus.OVERPAID

    should_credit = new_status in (
        FundingOrderStatus.CREDITED,
        FundingOrderStatus.OVERPAID,
    ) and received > 0

    now_iso = datetime.now(UTC).isoformat()
    raw = (
        payload.raw_payload
        if payload.raw_payload is not None
        else payload.model_dump(mode="json")
    )

    event_data: dict = {
        "funding_order_id": order_id,
        "provider_event_id": payload.provider_event_id,
        "provider_status": payload.status,
        "received_amount": float(received),
        "raw_payload": raw,
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
        client, payload.provider_event_id
    )
    assert refreshed is not None
    return _event_response(refreshed)
