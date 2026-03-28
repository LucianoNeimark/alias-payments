"""Inbound webhooks (e.g. Talo)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from supabase import Client

from app.database import get_supabase_client
from app.schemas.funding import FundingEventResponse, TaloWebhookPayload
from app.services import webhook_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.post("/talo", response_model=FundingEventResponse)
async def talo_webhook(
    body: TaloWebhookPayload,
    client: SupabaseDep,
) -> FundingEventResponse:
    return await webhook_service.process_talo_webhook(client, body)
