"""Pydantic schemas for the feedback feature."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """Sent by the bot — user is upserted by telegram_id (same as /bot/events)."""

    telegram_id: int
    telegram_username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: str | None = None
    text: str = Field(min_length=5, max_length=4000)


class FeedbackRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    text: str
    language: str | None
    is_resolved: bool
    created_at: datetime

    # Enriched on read
    user_first_name: str | None = None
    user_telegram_username: str | None = None
    user_telegram_id: int | None = None


class FeedbackList(BaseModel):
    total: int
    items: list[FeedbackRow]
