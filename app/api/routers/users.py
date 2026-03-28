"""User HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.database import get_supabase_client
from app.schemas.users import (
    UserCreate,
    UserResponse,
    UserStatusUpdate,
    UserWithWalletResponse,
)
from app.services import user_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.post(
    "/register",
    response_model=UserWithWalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    client: SupabaseDep,
) -> UserWithWalletResponse:
    return user_service.register_user(client, payload)


@router.get("/by-auth/{auth_provider_user_id}", response_model=UserResponse)
def get_user_by_auth(
    auth_provider_user_id: str,
    client: SupabaseDep,
) -> UserResponse:
    return user_service.get_user_by_auth_provider(client, auth_provider_user_id)


@router.get("/", response_model=list[UserResponse])
def list_users(
    client: SupabaseDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserResponse]:
    return user_service.list_users(client, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, client: SupabaseDep) -> UserResponse:
    return user_service.get_user(client, user_id)


@router.patch("/{user_id}/status", response_model=UserResponse)
def patch_user_status(
    user_id: str,
    body: UserStatusUpdate,
    client: SupabaseDep,
) -> UserResponse:
    return user_service.update_status(client, user_id, body.status)
