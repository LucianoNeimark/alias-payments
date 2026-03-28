"""Agent table access via Supabase."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client


def create_agent(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("agents").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no agent row")
    return rows[0]


def get_agent_by_id(client: Client, agent_id: str) -> dict[str, Any] | None:
    response = (
        client.table("agents").select("*").eq("id", agent_id).limit(1).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_agents_by_user_id(client: Client, user_id: str) -> list[dict[str, Any]]:
    response = (
        client.table("agents")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )
    return list(response.data or [])


def update_agent(
    client: Client, agent_id: str, patch: dict[str, Any]
) -> dict[str, Any] | None:
    now = datetime.now(UTC).isoformat()
    payload = {**patch, "updated_at": now}
    response = (
        client.table("agents").update(payload).eq("id", agent_id).execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
