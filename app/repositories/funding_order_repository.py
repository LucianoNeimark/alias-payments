"""Funding orders table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_order(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("funding_orders").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no funding_order row")
    return rows[0]


def get_order_by_id(client: Client, order_id: str) -> dict[str, Any] | None:
    response = (
        client.table("funding_orders")
        .select("*")
        .eq("id", order_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_orders_by_user(
    client: Client, user_id: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    end = max(offset + limit - 1, offset)
    response = (
        client.table("funding_orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, end)
        .execute()
    )
    return list(response.data or [])


def update_order_status(
    client: Client,
    order_id: str,
    status: str,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    patch: dict[str, Any] = {"status": status, "updated_at": now}
    if extra_fields:
        patch.update(extra_fields)
    response = (
        client.table("funding_orders").update(patch).eq("id", order_id).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
