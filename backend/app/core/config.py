"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # In Docker the env vars are injected directly (env_file: ../.env in compose),
    # so the .env file path is best-effort — ignored if not present.
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", "/app/.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "nasiya-backend"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = Field(
        default="postgresql+asyncpg://nasiya:nasiya_dev_pw@localhost:5433/nasiya",
        description="Async SQLAlchemy URL used by the app",
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg://nasiya:nasiya_dev_pw@localhost:5433/nasiya",
        description="Sync URL used by Alembic migrations",
    )
    redis_url: str = "redis://localhost:6380/0"

    secret_key: str = "change-me-32-bytes-hex"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Trusted internal token used by the dashboard for write endpoints
    # before the user-facing login UI exists. Sent as `X-Service-Token`.
    service_token: str = ""

    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    bot_token: str = ""
    bot_admin_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("bot_admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, v: object) -> object:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
