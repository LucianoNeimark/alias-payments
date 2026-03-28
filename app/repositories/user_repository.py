"""User table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_user(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    """Insert a user row and return the inserted record."""
    response = client.table("users").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no user row")
    return rows[0]


def get_user_by_id(client: Client, user_id: str) -> dict[str, Any] | None:
    response = (
        client.table("users").select("*").eq("id", user_id).limit(1).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_user_by_auth_provider_id(
    client: Client, auth_provider_user_id: str
) -> dict[str, Any] | None:
    response = (
        client.table("users")
        .select("*")
        .eq("auth_provider_user_id", auth_provider_user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_users(client: Client, limit: int, offset: int) -> list[dict[str, Any]]:
    end = max(offset + limit - 1, offset)
    response = (
        client.table("users")
        .select("*")
        .order("created_at", desc=False)
        .range(offset, end)
        .execute()
    )
    return list(response.data or [])


def update_user_status(
    client: Client, user_id: str, status: str
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    payload = {"status": status, "updated_at": now}
    response = (
        client.table("users").update(payload).eq("id", user_id).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
