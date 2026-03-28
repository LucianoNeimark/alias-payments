"""Wallet HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from supabase import Client

from app.database import get_supabase_client
from app.schemas.wallets import WalletResponse
from app.services import wallet_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.get("/{user_id}", response_model=WalletResponse)
def get_wallet(user_id: str, client: SupabaseDep) -> WalletResponse:
    return wallet_service.get_wallet_for_user(client, user_id)
