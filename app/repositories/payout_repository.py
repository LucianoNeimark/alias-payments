"""Payouts table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_payout(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("payouts").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no payout row")
    return rows[0]


def get_by_id(client: Client, payout_id: str) -> dict[str, Any] | None:
    response = (
        client.table("payouts").select("*").eq("id", payout_id).limit(1).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_latest_for_payment_request(
    client: Client, payment_request_id: str
) -> dict[str, Any] | None:
    response = (
        client.table("payouts")
        .select("*")
        .eq("payment_request_id", payment_request_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_payouts(
    client: Client,
    limit: int,
    offset: int,
    payment_request_id: str | None = None,
) -> list[dict[str, Any]]:
    end = max(offset + limit - 1, offset)
    q = (
        client.table("payouts")
        .select("*")
        .order("created_at", desc=True)
    )
    if payment_request_id is not None:
        q = q.eq("payment_request_id", payment_request_id)
    response = q.range(offset, end).execute()
    return list(response.data or [])


def update_payout(
    client: Client, payout_id: str, patch: dict[str, Any]
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    payload = {**patch, "updated_at": now}
    response = (
        client.table("payouts").update(payload).eq("id", payout_id).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
