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


def list_queued_payouts(client: Client, limit: int = 20) -> list[dict[str, Any]]:
    """Payouts waiting for execution, oldest first."""
    capped = max(limit, 1)
    response = (
        client.table("payouts")
        .select("*")
        .eq("status", "queued")
        .order("created_at", desc=False)
        .limit(capped)
        .execute()
    )
    return list(response.data or [])


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


def list_payouts_for_user(
    client: Client, user_id: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    """Payout rows for payment requests owned by ``user_id`` (inner join)."""
    end = max(offset + limit - 1, offset)
    response = (
        client.table("payouts")
        .select("*, payment_requests!inner(user_id)")
        .eq("payment_requests.user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, end)
        .execute()
    )
    rows: list[dict[str, Any]] = list(response.data or [])
    for row in rows:
        row.pop("payment_requests", None)
    return rows


def count_for_user_by_status(
    client: Client, user_id: str, payout_status: str
) -> int:
    response = (
        client.table("payouts")
        .select("id, payment_requests!inner(user_id)", count="exact")
        .eq("payment_requests.user_id", user_id)
        .eq("status", payout_status)
        .execute()
    )
    return int(response.count or 0)


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
