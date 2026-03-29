"""Supabase JWT authentication for dashboard / human users."""

from __future__ import annotations

import logging
import time
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from supabase import Client

from app.config import get_settings
from app.database import get_supabase_client
from app.repositories import user_repository

logger = logging.getLogger(__name__)

_jwks_cache: dict | None = None
_jwks_cache_ts: float = 0.0
_JWKS_TTL = 300  # seconds


def _fetch_jwks() -> dict:
    """Fetch JWKS from Supabase and cache for 5 minutes."""
    global _jwks_cache, _jwks_cache_ts
    now = time.time()
    if _jwks_cache is not None and (now - _jwks_cache_ts) < _JWKS_TTL:
        return _jwks_cache

    settings = get_settings()
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    import urllib.request, json

    try:
        with urllib.request.urlopen(jwks_url, timeout=5) as resp:
            data = json.loads(resp.read())
        _jwks_cache = data
        _jwks_cache_ts = now
        logger.info("Fetched JWKS from %s (%d keys)", jwks_url, len(data.get("keys", [])))
        return data
    except Exception as exc:
        logger.warning("Failed to fetch JWKS from %s: %s", jwks_url, exc)
        if _jwks_cache is not None:
            return _jwks_cache
        raise


def _get_signing_key(token: str) -> jwt.algorithms.ECAlgorithm | str:
    """Resolve the signing key for a token from JWKS or the legacy HS256 secret."""
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "")

    if alg == "ES256":
        jwks_data = _fetch_jwks()
        from jwt import PyJWKClient, PyJWK

        jwk_set = PyJWKClient("")
        jwk_set._jwks = jwks_data
        kid = header.get("kid")
        for key_data in jwks_data.get("keys", []):
            if key_data.get("kid") == kid or kid is None:
                signing_key = PyJWK.from_dict(key_data)
                return signing_key.key
        raise InvalidTokenError(f"No matching key found for kid={kid}")

    if alg == "HS256":
        settings = get_settings()
        secret = settings.supabase_jwt_secret
        if not secret:
            raise InvalidTokenError("No HS256 secret configured")
        return secret

    raise InvalidTokenError(f"Unsupported algorithm: {alg}")


def get_bearer_token(request: Request) -> str | None:
    raw = (request.headers.get("Authorization") or "").strip()
    if raw.lower().startswith("bearer "):
        return raw[7:].strip() or None
    return None


def decode_supabase_access_token(token: str) -> dict:
    """Verify access token issued by Supabase Auth (ES256 or HS256)."""
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        key = _get_signing_key(token)
        return jwt.decode(
            token,
            key,
            algorithms=[alg],
            audience="authenticated",
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def token_valid_for_middleware(token: str) -> bool:
    """Lightweight check for API key middleware."""
    try:
        decode_supabase_access_token(token)
        return True
    except Exception:
        return False


async def get_current_user(
    request: Request,
    client: Client = Depends(get_supabase_client),
) -> dict:
    token = get_bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization bearer token",
        )
    claims = decode_supabase_access_token(token)
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )
    user = user_repository.get_user_by_auth_provider_id(client, str(sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No app profile linked to this account; call POST /users/register first",
        )
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]
