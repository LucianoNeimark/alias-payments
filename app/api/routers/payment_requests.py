"""Payment request HTTP routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.database import get_supabase_client
from app.schemas.approvals import ApprovalResponse
from app.schemas.payment_requests import (
    PaymentRequestApprove,
    PaymentRequestCreate,
    PaymentRequestReject,
    PaymentRequestResponse,
)
from app.services import approval_service, payment_request_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.post(
    "/",
    response_model=PaymentRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_request(
    payload: PaymentRequestCreate,
    client: SupabaseDep,
) -> PaymentRequestResponse:
    return payment_request_service.create_payment_request(client, payload)


@router.get("/", response_model=list[PaymentRequestResponse])
def list_payment_requests(
    client: SupabaseDep,
    user_id: Annotated[UUID, Query(description="Owner user id")],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PaymentRequestResponse]:
    return payment_request_service.list_payment_requests_for_user(
        client, str(user_id), limit=limit, offset=offset
    )


@router.get("/{payment_request_id}", response_model=PaymentRequestResponse)
def get_payment_request(
    payment_request_id: str,
    client: SupabaseDep,
) -> PaymentRequestResponse:
    return payment_request_service.get_payment_request(client, payment_request_id)


@router.get(
    "/{payment_request_id}/approvals",
    response_model=list[ApprovalResponse],
)
def list_approvals(
    payment_request_id: str,
    client: SupabaseDep,
) -> list[ApprovalResponse]:
    payment_request_service.get_payment_request(client, payment_request_id)
    return approval_service.list_approvals_for_payment_request(
        client, payment_request_id
    )


@router.post(
    "/{payment_request_id}/approve",
    response_model=PaymentRequestResponse,
)
def approve_payment_request(
    payment_request_id: str,
    body: PaymentRequestApprove,
    client: SupabaseDep,
) -> PaymentRequestResponse:
    return payment_request_service.approve_payment_request(
        client, payment_request_id, body
    )


@router.post(
    "/{payment_request_id}/reject",
    response_model=PaymentRequestResponse,
)
def reject_payment_request(
    payment_request_id: str,
    body: PaymentRequestReject,
    client: SupabaseDep,
) -> PaymentRequestResponse:
    return payment_request_service.reject_payment_request(
        client, payment_request_id, body
    )
