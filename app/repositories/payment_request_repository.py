"""Payment requests table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_payment_request(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("payment_requests").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no payment_request row")
    return rows[0]


def get_by_id(client: Client, payment_request_id: str) -> dict[str, Any] | None:
    response = (
        client.table("payment_requests")
        .select("*")
        .eq("id", payment_request_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_by_idempotency_key(
    client: Client, idempotency_key: str
) -> dict[str, Any] | None:
    response = (
        client.table("payment_requests")
        .select("*")
        .eq("idempotency_key", idempotency_key)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_by_user_id(
    client: Client,
    user_id: str,
    limit: int,
    offset: int,
    *,
    status: str | None = None,
) -> list[dict[str, Any]]:
    end = max(offset + limit - 1, offset)
    q = (
        client.table("payment_requests")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if status is not None:
        q = q.eq("status", status)
    response = q.range(offset, end).execute()
    return list(response.data or [])


def count_by_user_id_and_status(
    client: Client, user_id: str, status: str
) -> int:
    response = (
        client.table("payment_requests")
        .select("*", count="exact")
        .eq("user_id", user_id)
        .eq("status", status)
        .execute()
    )
    return int(response.count or 0)


def update_payment_request(
    client: Client, payment_request_id: str, patch: dict[str, Any]
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    payload = {**patch, "updated_at": now}
    response = (
        client.table("payment_requests")
        .update(payload)
        .eq("id", payment_request_id)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
