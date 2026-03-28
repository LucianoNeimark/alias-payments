"""Mock Talo client: replace with real API integration when available."""

import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4


def create_payment(user_id: str, amount: Decimal, currency: str) -> dict:
    """
    Simulate provider call that provisions a CVU for a funding order.

    Returns provider_payment_id, cvu, alias, expires_at (ISO string).
    """
    _ = user_id, amount, currency  # unused in mock; real API would use these
    payment_id = str(uuid4())
    cvu = "".join(str(secrets.randbelow(10)) for _ in range(22))
    suffix = secrets.token_hex(3)
    alias = f"agentpay.demo.{suffix}"
    expires_at = datetime.now(UTC) + timedelta(hours=24)
    return {
        "provider_payment_id": payment_id,
        "cvu": cvu,
        "alias": alias,
        "expires_at": expires_at.isoformat(),
    }
