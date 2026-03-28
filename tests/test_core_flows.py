"""Five core business-logic integration tests against the real Supabase instance."""

from __future__ import annotations

import uuid
from decimal import Decimal

from tests.conftest import create_agent, fund_wallet, register_user, track


# ---------------------------------------------------------------------------
# 1. Funding credits wallet
# ---------------------------------------------------------------------------
def test_funding_credits_wallet(client, created_ids):
    """Fund 10 000 ARS via funding order + webhook and verify wallet + ledger."""
    user, wallet = register_user(client, created_ids)
    user_id = user["id"]
    wallet_id = wallet["id"]

    order = fund_wallet(client, created_ids, user_id, 10_000)

    # Funding order should be credited
    resp = client.get(f"/funding-orders/{order['id']}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "credited"

    # Wallet balance should reflect the credit
    resp = client.get(f"/wallets/{user_id}")
    assert resp.status_code == 200
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("10000")
    assert Decimal(str(w["reserved_balance"])) == Decimal("0")

    # Ledger should have exactly one funding_credit entry
    resp = client.get(f"/ledger/{wallet_id}")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 1
    e = entries[0]
    assert e["entry_type"] == "funding_credit"
    assert e["direction"] == "credit"
    assert Decimal(str(e["amount"])) == Decimal("10000")
    track(created_ids, "ledger_entries", e["id"])


# ---------------------------------------------------------------------------
# 2. Full payment happy path (fund -> request -> approve -> execute payout)
# ---------------------------------------------------------------------------
def test_full_payment_happy_path(client, created_ids):
    """Complete flow: fund 10 000, pay 1 200, verify balances and ledger."""
    user, wallet = register_user(client, created_ids)
    user_id = user["id"]
    wallet_id = wallet["id"]

    fund_wallet(client, created_ids, user_id, 10_000)
    agent = create_agent(client, created_ids, user_id)

    # Create payment request
    idem_key = f"idem_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        "/payment-requests",
        json={
            "user_id": user_id,
            "agent_id": agent["id"],
            "amount": 1200,
            "destination_cvu": "0000000000000000000001",
            "purpose": "Integration test payment",
            "idempotency_key": idem_key,
        },
    )
    assert resp.status_code == 201, resp.text
    pr = resp.json()
    track(created_ids, "payment_requests", pr["id"])
    assert pr["status"] == "requested"

    # Approve -> reserves funds and creates payout
    resp = client.post(
        f"/payment-requests/{pr['id']}/approve",
        json={"user_id": user_id},
    )
    assert resp.status_code == 200, resp.text
    pr = resp.json()
    assert pr["status"] == "reserved"

    # Wallet should show reserved balance
    resp = client.get(f"/wallets/{user_id}")
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("8800")
    assert Decimal(str(w["reserved_balance"])) == Decimal("1200")

    # Get the queued payout
    resp = client.get("/payouts", params={"payment_request_id": pr["id"]})
    assert resp.status_code == 200
    payouts = resp.json()
    assert len(payouts) == 1
    payout = payouts[0]
    track(created_ids, "payouts", payout["id"])
    assert payout["status"] == "queued"

    # Execute payout (mock bank success)
    resp = client.post(f"/payouts/{payout['id']}/execute")
    assert resp.status_code == 200, resp.text
    payout = resp.json()
    assert payout["status"] == "completed"

    # Payment request should be completed
    resp = client.get(f"/payment-requests/{pr['id']}")
    assert resp.json()["status"] == "completed"

    # Final wallet: available = 8800, reserved = 0
    resp = client.get(f"/wallets/{user_id}")
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("8800")
    assert Decimal(str(w["reserved_balance"])) == Decimal("0")

    # Ledger should have 3 entries: funding_credit, reserve, payout_debit
    resp = client.get(f"/ledger/{wallet_id}")
    entries = resp.json()
    types = sorted([e["entry_type"] for e in entries])
    assert types == ["funding_credit", "payout_debit", "reserve"]
    for e in entries:
        track(created_ids, "ledger_entries", e["id"])


# ---------------------------------------------------------------------------
# 3. Approve payment with insufficient funds
# ---------------------------------------------------------------------------
def test_approve_payment_insufficient_funds(client, created_ids):
    """Approve on an unfunded wallet returns 400 and sets insufficient_funds."""
    user, wallet = register_user(client, created_ids)
    user_id = user["id"]
    agent = create_agent(client, created_ids, user_id)

    idem_key = f"idem_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        "/payment-requests",
        json={
            "user_id": user_id,
            "agent_id": agent["id"],
            "amount": 5000,
            "destination_cvu": "0000000000000000000002",
            "purpose": "Should fail - no funds",
            "idempotency_key": idem_key,
        },
    )
    assert resp.status_code == 201, resp.text
    pr = resp.json()
    track(created_ids, "payment_requests", pr["id"])

    # Approve should fail with 400
    resp = client.post(
        f"/payment-requests/{pr['id']}/approve",
        json={"user_id": user_id},
    )
    assert resp.status_code == 400

    # PR status should be insufficient_funds
    resp = client.get(f"/payment-requests/{pr['id']}")
    assert resp.json()["status"] == "insufficient_funds"

    # Wallet remains untouched
    resp = client.get(f"/wallets/{user_id}")
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("0")
    assert Decimal(str(w["reserved_balance"])) == Decimal("0")


# ---------------------------------------------------------------------------
# 4. Reject payment request
# ---------------------------------------------------------------------------
def test_reject_payment_request(client, created_ids):
    """Reject a payment request: no funds move, approval record created."""
    user, wallet = register_user(client, created_ids)
    user_id = user["id"]

    fund_wallet(client, created_ids, user_id, 5_000)
    agent = create_agent(client, created_ids, user_id)

    idem_key = f"idem_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        "/payment-requests",
        json={
            "user_id": user_id,
            "agent_id": agent["id"],
            "amount": 1500,
            "destination_cvu": "0000000000000000000003",
            "purpose": "Will be rejected",
            "idempotency_key": idem_key,
        },
    )
    assert resp.status_code == 201, resp.text
    pr = resp.json()
    track(created_ids, "payment_requests", pr["id"])

    # Reject
    resp = client.post(
        f"/payment-requests/{pr['id']}/reject",
        json={"user_id": user_id, "decision_reason": "Not authorized"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "rejected"

    # Wallet unchanged
    resp = client.get(f"/wallets/{user_id}")
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("5000")
    assert Decimal(str(w["reserved_balance"])) == Decimal("0")

    # Approval record exists with decision=rejected
    resp = client.get(f"/payment-requests/{pr['id']}/approvals")
    assert resp.status_code == 200
    approvals = resp.json()
    assert len(approvals) == 1
    assert approvals[0]["decision"] == "rejected"
    track(created_ids, "approvals", approvals[0]["id"])


# ---------------------------------------------------------------------------
# 5. Payout failure releases reserved funds
# ---------------------------------------------------------------------------
def test_payout_failure_releases_reserved_funds(client, created_ids):
    """Bank failure releases reserved funds back to available via ledger."""
    user, wallet = register_user(client, created_ids)
    user_id = user["id"]
    wallet_id = wallet["id"]

    fund_wallet(client, created_ids, user_id, 5_000)
    agent = create_agent(client, created_ids, user_id)

    idem_key = f"idem_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        "/payment-requests",
        json={
            "user_id": user_id,
            "agent_id": agent["id"],
            "amount": 1200,
            "destination_cvu": "0000000000000000000004",
            "purpose": "Will fail at bank",
            "idempotency_key": idem_key,
        },
    )
    assert resp.status_code == 201, resp.text
    pr = resp.json()
    track(created_ids, "payment_requests", pr["id"])

    # Approve (reserves 1200)
    resp = client.post(
        f"/payment-requests/{pr['id']}/approve",
        json={"user_id": user_id},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "reserved"

    # Get payout
    resp = client.get("/payouts", params={"payment_request_id": pr["id"]})
    payout = resp.json()[0]
    track(created_ids, "payouts", payout["id"])

    # Execute with forced failure
    resp = client.post(
        f"/payouts/{payout['id']}/execute",
        headers={"X-Mock-Failure": "true"},
    )
    assert resp.status_code == 200, resp.text
    payout = resp.json()
    assert payout["status"] == "failed"

    # Payment request should be failed
    resp = client.get(f"/payment-requests/{pr['id']}")
    assert resp.json()["status"] == "failed"

    # Wallet: funds fully released back to available
    resp = client.get(f"/wallets/{user_id}")
    w = resp.json()
    assert Decimal(str(w["available_balance"])) == Decimal("5000")
    assert Decimal(str(w["reserved_balance"])) == Decimal("0")

    # Ledger should show funding_credit, reserve, release
    resp = client.get(f"/ledger/{wallet_id}")
    entries = resp.json()
    types = sorted([e["entry_type"] for e in entries])
    assert types == ["funding_credit", "release", "reserve"]
    for e in entries:
        track(created_ids, "ledger_entries", e["id"])
