"""Approvals table access via Supabase."""

from typing import Any

from supabase import Client


def create_approval(client: Client, data: dict[str, Any]) -> dict[str, Any]:
    response = client.table("approvals").insert(data).execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("Insert returned no approval row")
    return rows[0]


def get_approvals_for_payment_request(
    client: Client, payment_request_id: str
) -> list[dict[str, Any]]:
    response = (
        client.table("approvals")
        .select("*")
        .eq("payment_request_id", payment_request_id)
        .order("created_at", desc=False)
        .execute()
    )
    return list(response.data or [])
