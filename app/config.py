"""Application settings loaded from environment variables."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_key: str
    database_url: str
    agentpay_api_key: str | None = None

    talo_user_id: str
    talo_client_id: str
    talo_client_secret: str
    talo_base_url: str = "https://sandbox-api.talo.com.ar"
    talo_webhook_url: str = ""

    # External MP transfer microservice (Selenium); optional for dev/tests
    payments_service_url: str | None = None
    payments_service_api_key: str | None = None
    payments_service_timeout: float = 60.0
    payments_service_verify_ssl: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


def resolve_payments_service_config() -> tuple[str | None, str | None, float, bool]:
    """URL, API key, and timeout for the MP transfer HTTP service.

    For ``PAYMENTS_SERVICE_URL`` and ``PAYMENTS_SERVICE_API_KEY`` only, a value
    in the repo root ``.env`` wins over the process environment. That avoids a
    stale export in the shell (e.g. truncated ngrok host) overriding what you
    set in ``.env``. If the key is absent or empty in ``.env``, the environment
    is used (for deployments without a dotenv file).
    """
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    file_vals: dict[str, str | None] = {}
    if env_path.is_file():
        file_vals = dotenv_values(env_path)

    def _pick(name: str) -> str | None:
        raw = file_vals.get(name)
        if raw is not None and str(raw).strip() != "":
            return str(raw).strip()
        return (os.environ.get(name) or "").strip() or None

    url = _pick("PAYMENTS_SERVICE_URL")
    api_key = _pick("PAYMENTS_SERVICE_API_KEY")
    timeout = 60.0
    tv = _pick("PAYMENTS_SERVICE_TIMEOUT")
    if tv:
        try:
            timeout = float(tv)
        except ValueError:
            pass
    verify_ssl = True
    vs = _pick("PAYMENTS_SERVICE_VERIFY_SSL")
    if vs and vs.lower() in ("0", "false", "no"):
        verify_ssl = False
    return url, api_key, timeout, verify_ssl
