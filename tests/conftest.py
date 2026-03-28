"""Shared fixtures for integration tests against the real Supabase instance."""

from __future__ import annotations

import uuid
from collections import defaultdict

import pytest
from fastapi.testclient import TestClient

from app.database import get_supabase_client
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def supabase():
    return get_supabase_client()


@pytest.fixture
def created_ids(supabase):
    """Collect entity ids during a test; delete them all on teardown."""
    cleanup_order = [
        "ledger_entries",
        "payouts",
        "approvals",
        "payment_requests",
        "funding_events",
        "funding_orders",
        "agents",
        "wallets",
        "users",
    ]
    tracker: dict[str, list[str]] = defaultdict(list)
    yield tracker
    for table in cleanup_order:
        for row_id in tracker.get(table, []):
            try:
                supabase.table(table).delete().eq("id", row_id).execute()
            except Exception:
                pass


def track(created_ids: dict, table: str, row_id: str) -> None:
    created_ids[table].append(row_id)


def register_user(client: TestClient, created_ids: dict) -> tuple[dict, dict]:
    """Register a user + wallet via the API and track for cleanup."""
    suffix = uuid.uuid4().hex[:8]
    resp = client.post(
        "/users/register",
        json={
            "auth_provider_user_id": f"test_{suffix}",
            "email": f"test_{suffix}@example.com",
            "username": f"testuser_{suffix}",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    user = data["user"]
    wallet = data["wallet"]
    track(created_ids, "users", user["id"])
    track(created_ids, "wallets", wallet["id"])
    return user, wallet


def fund_wallet(
    client: TestClient,
    created_ids: dict,
    user_id: str,
    amount: float,
) -> dict:
    """Create a funding order + simulate webhook credit for the given amount."""
    resp = client.post(
        "/funding-orders",
        json={
            "user_id": user_id,
            "requested_amount": amount,
            "currency": "ARS",
        },
    )
    assert resp.status_code == 201, resp.text
    order = resp.json()
    track(created_ids, "funding_orders", order["id"])

    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        "/webhooks/talo",
        json={
            "provider_event_id": event_id,
            "funding_order_id": order["id"],
            "status": "SUCCESS",
            "received_amount": amount,
        },
    )
    assert resp.status_code == 200, resp.text
    event = resp.json()
    track(created_ids, "funding_events", event["id"])
    return order


def create_agent(
    client: TestClient,
    created_ids: dict,
    user_id: str,
    *,
    spending_limit: float | None = None,
) -> dict:
    payload: dict = {"user_id": user_id, "name": f"agent_{uuid.uuid4().hex[:6]}"}
    if spending_limit is not None:
        payload["default_spending_limit"] = spending_limit
    resp = client.post("/agents", json=payload)
    assert resp.status_code == 201, resp.text
    agent = resp.json()
    track(created_ids, "agents", agent["id"])
    return agent
