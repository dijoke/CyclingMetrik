from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://coaching:coaching@localhost:5432/coaching"
    token_encryption_key: str
    garmin_client_id: str = ""
    garmin_client_secret: str = ""
    strava_client_id: str = ""
    strava_client_secret: str = ""
    nolio_client_id: str = ""
    nolio_client_secret: str = ""
    frontend_base_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
