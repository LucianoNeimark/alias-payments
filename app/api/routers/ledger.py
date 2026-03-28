"""Ledger HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.database import get_supabase_client
from app.schemas.ledger import LedgerEntryResponse
from app.services import ledger_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.get("/{wallet_id}", response_model=list[LedgerEntryResponse])
def list_ledger_entries(
    wallet_id: str,
    client: SupabaseDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[LedgerEntryResponse]:
    return ledger_service.get_entries_for_wallet(
        client, wallet_id, limit=limit, offset=offset
    )
