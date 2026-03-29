"""Payout HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from supabase import Client

from app.database import get_supabase_client
from app.schemas.payouts import PayoutResponse
from app.services import payout_service
from app.services.payments_client import get_payments_client

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.get("/payments-health")
async def payments_health() -> dict[str, str]:
    """Probe the external MP transfer microservice (no auth on upstream /health)."""
    client = get_payments_client()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de pagos no configurado",
        )
    healthy = await client.health()
    if not healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de pagos no disponible",
        )
    return {"payments_service": "ok"}


@router.get("/", response_model=list[PayoutResponse])
def list_payouts(
    client: SupabaseDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    payment_request_id: Annotated[
        str | None, Query(description="Filter by payment request id")
    ] = None,
) -> list[PayoutResponse]:
    return payout_service.list_payouts(
        client,
        limit=limit,
        offset=offset,
        payment_request_id=payment_request_id,
    )


@router.get("/{payout_id}", response_model=PayoutResponse)
def get_payout(payout_id: str, client: SupabaseDep) -> PayoutResponse:
    return payout_service.get_payout(client, payout_id)


@router.post("/{payout_id}/execute", response_model=PayoutResponse)
async def execute_payout(
    payout_id: str,
    client: SupabaseDep,
    x_mock_failure: Annotated[str | None, Header(alias="X-Mock-Failure")] = None,
    x_mock_manual_review: Annotated[
        str | None, Header(alias="X-Mock-Manual-Review")
    ] = None,
) -> PayoutResponse:
    force_failure = (x_mock_failure or "").lower() in ("1", "true", "yes")
    force_manual = (x_mock_manual_review or "").lower() in ("1", "true", "yes")
    return await payout_service.execute_payout(
        client,
        payout_id,
        force_failure=force_failure,
        force_manual_review=force_manual,
    )


@router.post("/{payout_id}/retry", response_model=PayoutResponse)
async def retry_payout(
    payout_id: str,
    client: SupabaseDep,
    x_mock_failure: Annotated[str | None, Header(alias="X-Mock-Failure")] = None,
    x_mock_manual_review: Annotated[
        str | None, Header(alias="X-Mock-Manual-Review")
    ] = None,
) -> PayoutResponse:
    force_failure = (x_mock_failure or "").lower() in ("1", "true", "yes")
    force_manual = (x_mock_manual_review or "").lower() in ("1", "true", "yes")
    return await payout_service.retry_payout(
        client,
        payout_id,
        force_failure=force_failure,
        force_manual_review=force_manual,
    )
