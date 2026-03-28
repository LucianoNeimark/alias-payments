"""Wallet domain service."""

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import wallet_repository
from app.schemas.wallets import WalletResponse


def get_wallet_for_user(client: Client, user_id: str) -> WalletResponse:
    row = wallet_repository.get_wallet_by_user_id(client, user_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for this user",
        )
    return WalletResponse.model_validate(row)
