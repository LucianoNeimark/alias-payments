"""Wallet table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_wallet(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    """Insert a wallet row and return the inserted record."""
    response = client.table("wallets").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no wallet row")
    return rows[0]


def get_wallet_by_user_id(client: Client, user_id: str) -> dict[str, Any] | None:
    response = (
        client.table("wallets")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_wallet_by_id(client: Client, wallet_id: str) -> dict[str, Any] | None:
    response = (
        client.table("wallets").select("*").eq("id", wallet_id).limit(1).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def update_wallet(
    client: Client, wallet_id: str, patch: dict[str, Any]
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    payload = {**patch, "updated_at": now}
    response = (
        client.table("wallets").update(payload).eq("id", wallet_id).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
