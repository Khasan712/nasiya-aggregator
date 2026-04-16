"""Bot runtime configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class BotSettings(BaseSettings):
    # See backend/app/core/config.py — env vars come from compose env_file in
    # Docker; the .env files below are best-effort fallbacks for local runs.
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR.parent / ".env", ROOT_DIR / ".env", "/app/.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = ""
    bot_admin_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)
    backend_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6380/0"
    # Same value as backend SERVICE_TOKEN — used to POST /bot/events
    service_token: str = ""

    @field_validator("bot_admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, v: object) -> object:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


settings = BotSettings()
