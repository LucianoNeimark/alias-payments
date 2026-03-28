"""Funding events table access via Supabase."""

from typing import Any

from supabase import Client


def create_event(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("funding_events").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no funding_event row")
    return rows[0]


def get_event_by_provider_event_id(
    client: Client, provider_event_id: str
) -> dict[str, Any] | None:
    response = (
        client.table("funding_events")
        .select("*")
        .eq("provider_event_id", provider_event_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
