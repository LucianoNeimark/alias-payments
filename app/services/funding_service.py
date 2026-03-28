"""Funding order domain service."""

from uuid import uuid4

from fastapi import HTTPException, status
from supabase import Client

from app.config import get_settings
from app.repositories import funding_order_repository, user_repository, wallet_repository
from app.schemas.funding import (
    FundingOrderCreate,
    FundingOrderResponse,
    FundingOrderStatus,
)
from app.services import talo_client


def _order_response(row: dict) -> FundingOrderResponse:
    return FundingOrderResponse.model_validate(row)


async def create_funding_order(
    client: Client, payload: FundingOrderCreate
) -> FundingOrderResponse:
    uid = str(payload.user_id)
    if not user_repository.get_user_by_id(client, uid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    wallet = wallet_repository.get_wallet_by_user_id(client, uid)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for user",
        )

    external_id = str(uuid4())
    settings = get_settings()

    talo = await talo_client.create_payment(
        amount=payload.requested_amount,
        currency=payload.currency,
        external_id=external_id,
        webhook_url=settings.talo_webhook_url,
    )

    row_data = {
        "user_id": uid,
        "wallet_id": str(wallet["id"]),
        "requested_amount": float(payload.requested_amount),
        "currency": payload.currency,
        "provider": "talo",
        "provider_payment_id": talo["provider_payment_id"],
        "cvu": talo["cvu"],
        "alias": talo["alias"],
        "status": FundingOrderStatus.PENDING.value,
        "expires_at": talo["expires_at"],
    }

    row = funding_order_repository.create_order(client, row_data)
    return _order_response(row)


def get_funding_order(client: Client, order_id: str) -> FundingOrderResponse:
    row = funding_order_repository.get_order_by_id(client, order_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding order not found",
        )
    return _order_response(row)


def list_funding_orders(
    client: Client, user_id: str, limit: int = 50, offset: int = 0
) -> list[FundingOrderResponse]:
    if not user_repository.get_user_by_id(client, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    capped = min(max(limit, 1), 100)
    rows = funding_order_repository.list_orders_by_user(
        client, user_id, capped, max(offset, 0)
    )
    return [_order_response(r) for r in rows]
