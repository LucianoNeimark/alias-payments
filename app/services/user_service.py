"""User domain service."""

from postgrest.exceptions import APIError

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import user_repository, wallet_repository
from app.schemas.users import (
    UserCreate,
    UserResponse,
    UserStatus,
    UserWithWalletResponse,
)
from app.schemas.wallets import WalletResponse


def _user_response(row: dict) -> UserResponse:
    return UserResponse.model_validate(row)


def register_user(client: Client, payload: UserCreate) -> UserWithWalletResponse:
    if user_repository.get_user_by_auth_provider_id(
        client, payload.auth_provider_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this auth_provider_user_id already exists",
        )

    user_row = {
        "auth_provider_user_id": payload.auth_provider_user_id,
        "email": str(payload.email),
        "username": payload.username,
        "status": UserStatus.ACTIVE.value,
    }

    try:
        user = user_repository.create_user(client, user_row)
    except APIError as exc:
        _raise_http_for_duplicate_auth(exc)

    wallet_row = {
        "user_id": str(user["id"]),
        "currency": "ARS",
        "available_balance": 0,
        "reserved_balance": 0,
    }

    try:
        wallet = wallet_repository.create_wallet(client, wallet_row)
    except Exception:
        # Best-effort cleanup if wallet creation fails after user insert
        try:
            client.table("users").delete().eq("id", user["id"]).execute()
        except Exception:
            pass
        raise

    return UserWithWalletResponse(
        user=_user_response(user),
        wallet=WalletResponse.model_validate(wallet),
    )


def _raise_http_for_duplicate_auth(exc: APIError) -> None:
    message = (getattr(exc, "message", None) or str(exc)).lower()
    if "unique" in message or "duplicate" in message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this auth_provider_user_id or email already exists",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc


def get_user(client: Client, user_id: str) -> UserResponse:
    row = user_repository.get_user_by_id(client, user_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return _user_response(row)


def get_user_by_auth_provider(
    client: Client, auth_provider_user_id: str
) -> UserResponse:
    row = user_repository.get_user_by_auth_provider_id(
        client, auth_provider_user_id
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return _user_response(row)


def list_users(
    client: Client, limit: int = 50, offset: int = 0
) -> list[UserResponse]:
    capped = min(max(limit, 1), 100)
    rows = user_repository.list_users(client, capped, max(offset, 0))
    return [_user_response(r) for r in rows]


def update_status(
    client: Client, user_id: str, new_status: UserStatus
) -> UserResponse:
    if not user_repository.get_user_by_id(client, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated = user_repository.update_user_status(
        client, user_id, new_status.value
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be updated",
        )
    return _user_response(updated)
