"""Inbound webhooks (e.g. Talo)."""

import hashlib
import hmac
import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from supabase import Client

from app.config import get_settings
from app.database import get_supabase_client
from app.schemas.funding import TaloWebhookPayload
from app.services import webhook_service

logger = logging.getLogger(__name__)

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


def _verify_talo_signature(raw_body: bytes, signature: str) -> None:
    """Validate HMAC-SHA256 signature sent by Talo in X-Talo-Signature."""
    settings = get_settings()
    expected = hmac.new(
        settings.talo_client_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )


@router.post("/talo", status_code=200)
async def talo_webhook(
    body: TaloWebhookPayload,
    request: Request,
    client: SupabaseDep,
    background_tasks: BackgroundTasks,
    x_talo_signature: str | None = Header(None),
) -> dict:
    logger.info(
        "talo webhook received: paymentId=%s externalId=%s message=%s",
        body.paymentId,
        body.externalId,
        body.message,
    )

    if x_talo_signature:
        raw_body = await request.body()
        _verify_talo_signature(raw_body, x_talo_signature)
    else:
        logger.debug("talo webhook: no X-Talo-Signature header (signature verification skipped)")

    background_tasks.add_task(
        webhook_service.process_talo_webhook_background, client, body
    )
    return {"status": "accepted"}
