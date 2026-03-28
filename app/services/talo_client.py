"""Talo Payments API client (sandbox / production)."""

from __future__ import annotations

import logging
import time
from decimal import Decimal

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_cached_token: str | None = None
_token_expires_at: float = 0.0

_TOKEN_LIFETIME_SECONDS = 3500


async def _get_token() -> str:
    """Obtain (or reuse cached) Bearer token from Talo."""
    global _cached_token, _token_expires_at

    if _cached_token and time.monotonic() < _token_expires_at:
        return _cached_token

    settings = get_settings()
    url = f"{settings.talo_base_url}/users/{settings.talo_user_id}/tokens"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json={
                "client_id": settings.talo_client_id,
                "client_secret": settings.talo_client_secret,
            },
            timeout=15.0,
        )
        resp.raise_for_status()

    data = resp.json().get("data", resp.json())
    token = data["token"]

    _cached_token = token
    _token_expires_at = time.monotonic() + _TOKEN_LIFETIME_SECONDS
    logger.info("talo_client: obtained new token")
    return token


async def create_payment(
    *,
    amount: Decimal,
    currency: str,
    external_id: str,
    webhook_url: str,
) -> dict:
    """
    Create a Talo payment order and return CVU details.

    Returns dict with keys: provider_payment_id, cvu, alias, expires_at.
    """
    settings = get_settings()
    token = await _get_token()

    payload = {
        "user_id": settings.talo_user_id,
        "price": {"amount": float(amount), "currency": currency},
        "payment_options": ["transfer"],
        "external_id": external_id,
        "webhook_url": webhook_url,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.talo_base_url}/payments/",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=20.0,
        )
        resp.raise_for_status()

    data = resp.json()["data"]
    quote = data["quotes"][0]
    cvu = quote.get("cvu") or quote.get("address", "")

    logger.info(
        "talo_client: payment created id=%s cvu=%s",
        data["id"],
        cvu[:8] + "...",
    )

    return {
        "provider_payment_id": data["id"],
        "cvu": cvu,
        "alias": quote.get("alias"),
        "expires_at": data.get("expiration_timestamp"),
    }


async def get_payment(payment_id: str) -> dict:
    """Fetch full payment details from Talo by their internal payment ID."""
    settings = get_settings()
    token = await _get_token()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.talo_base_url}/payments/{payment_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15.0,
        )
        resp.raise_for_status()

    return resp.json()["data"]


async def simulate_faucet(cvu: str, amount: float) -> None:
    """Hit the sandbox faucet to simulate an inbound transfer to a CVU."""
    settings = get_settings()
    token = await _get_token()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.talo_base_url}/cvu/{cvu}/faucet",
            headers={"Authorization": f"Bearer {token}"},
            json={"amount": amount},
            timeout=15.0,
        )
        resp.raise_for_status()

    logger.info("talo_client: faucet simulated amount=%s cvu=%s", amount, cvu[:8] + "...")
