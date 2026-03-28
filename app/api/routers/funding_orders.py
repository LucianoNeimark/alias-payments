"""Funding order HTTP routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.database import get_supabase_client
from app.schemas.funding import FundingOrderCreate, FundingOrderResponse
from app.services import funding_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.post(
    "/",
    response_model=FundingOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_funding_order(
    payload: FundingOrderCreate,
    client: SupabaseDep,
) -> FundingOrderResponse:
    return await funding_service.create_funding_order(client, payload)


@router.get("/", response_model=list[FundingOrderResponse])
def list_funding_orders(
    client: SupabaseDep,
    user_id: Annotated[UUID, Query(description="Owner user id")],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[FundingOrderResponse]:
    return funding_service.list_funding_orders(
        client, str(user_id), limit=limit, offset=offset
    )


@router.get("/{order_id}", response_model=FundingOrderResponse)
def get_funding_order(order_id: str, client: SupabaseDep) -> FundingOrderResponse:
    return funding_service.get_funding_order(client, order_id)
