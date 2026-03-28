"""Application settings loaded from environment variables."""

from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
