"""Ledger domain service: entries and wallet balance updates."""

from decimal import Decimal

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import ledger_repository, wallet_repository
from app.schemas.ledger import (
    LedgerCreateInternal,
    LedgerDirection,
    LedgerEntryResponse,
    LedgerEntryType,
)


def _decimal(val) -> Decimal:
    if val is None:
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _compute_ledger_row(
    available: Decimal,
    reserved: Decimal,
    payload: LedgerCreateInternal,
) -> tuple[Decimal, Decimal, LedgerDirection]:
    amount = payload.amount
    et = payload.entry_type

    if et == LedgerEntryType.FUNDING_CREDIT:
        return available + amount, reserved, LedgerDirection.CREDIT
    if et == LedgerEntryType.RESERVE:
        return available - amount, reserved + amount, LedgerDirection.DEBIT
    if et == LedgerEntryType.RELEASE:
        return available + amount, reserved - amount, LedgerDirection.CREDIT
    if et == LedgerEntryType.PAYOUT_DEBIT:
        return available, reserved - amount, LedgerDirection.DEBIT
    if et == LedgerEntryType.MANUAL_ADJUSTMENT:
        if payload.direction is None:
            raise ValueError("direction is required for manual_adjustment")
        if payload.direction == LedgerDirection.CREDIT:
            return available + amount, reserved, LedgerDirection.CREDIT
        return available - amount, reserved, LedgerDirection.DEBIT

    raise ValueError(f"Unsupported entry_type: {et}")


def record_entry(client: Client, payload: LedgerCreateInternal) -> LedgerEntryResponse:
    wallet_id_str = str(payload.wallet_id)
    wallet = wallet_repository.get_wallet_by_id(client, wallet_id_str)
    if not wallet:
        raise ValueError("Wallet not found")

    available = _decimal(wallet.get("available_balance"))
    reserved = _decimal(wallet.get("reserved_balance"))
    new_av, new_res, direction = _compute_ledger_row(available, reserved, payload)

    if new_av < 0 or new_res < 0:
        raise ValueError(
            "Operation would result in negative balance; insufficient funds or invalid state"
        )

    entry_data = {
        "wallet_id": wallet_id_str,
        "entry_type": payload.entry_type.value,
        "direction": direction.value,
        "amount": float(payload.amount),
        "currency": payload.currency,
        "reference_type": payload.reference_type,
        "reference_id": payload.reference_id,
        "balance_after_available": float(new_av),
        "balance_after_reserved": float(new_res),
        "description": payload.description,
    }

    entry = ledger_repository.create_entry(client, entry_data)
    try:
        updated = wallet_repository.update_wallet(
            client,
            wallet_id_str,
            {
                "available_balance": float(new_av),
                "reserved_balance": float(new_res),
            },
        )
        if not updated:
            raise RuntimeError("Wallet update returned no row")
    except Exception:
        try:
            client.table("ledger_entries").delete().eq("id", entry["id"]).execute()
        except Exception:
            pass
        raise

    return LedgerEntryResponse.model_validate(entry)


def get_entries_for_wallet(
    client: Client, wallet_id: str, limit: int = 50, offset: int = 0
) -> list[LedgerEntryResponse]:
    if not wallet_repository.get_wallet_by_id(client, wallet_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    capped = min(max(limit, 1), 100)
    rows = ledger_repository.list_entries_by_wallet_id(
        client, wallet_id, capped, max(offset, 0)
    )
    return [LedgerEntryResponse.model_validate(r) for r in rows]
