"""Ledger entries table access via Supabase."""

from typing import Any

from supabase import Client


def create_entry(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("ledger_entries").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no ledger entry row")
    return rows[0]


def list_entries_by_wallet_id(
    client: Client, wallet_id: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    end = max(offset + limit - 1, offset)
    response = (
        client.table("ledger_entries")
        .select("*")
        .eq("wallet_id", wallet_id)
        .order("created_at", desc=True)
        .range(offset, end)
        .execute()
    )
    return list(response.data or [])
