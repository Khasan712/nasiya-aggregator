"""Pydantic schemas for bot events + stats."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.event import BotEventType
from app.models.user import UserLanguage


class BotEventCreate(BaseModel):
    """Sent by the bot to record one user interaction."""

    telegram_id: int
    telegram_username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: UserLanguage | None = None
    event_type: BotEventType
    product_id: int | None = None
    payload: dict[str, Any] | None = None


class BotEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    event_type: BotEventType
    product_id: int | None
    payload: dict[str, Any] | None
    created_at: datetime


class StatsCounter(BaseModel):
    today: int
    last_7d: int
    last_30d: int
    total: int


class StatsTopProduct(BaseModel):
    product_id: int
    name_uz: str
    provider_name_uz: str
    views: int


class StatsAmountBucket(BaseModel):
    bucket_label: str
    count: int


class StatsDailyPoint(BaseModel):
    day: date
    events: int
    unique_users: int


class StatsEventTypeRow(BaseModel):
    event_type: str
    count: int


class StatsTopProvider(BaseModel):
    provider_id: int
    name_uz: str
    views: int


class StatsHourlyPoint(BaseModel):
    hour: int  # 0..23
    events: int


class StatsFunnelStep(BaseModel):
    name: str
    count: int


class StatsAmountSummary(BaseModel):
    searches: int
    avg_uzs: int
    median_uzs: int
    max_uzs: int


class StatsOverview(BaseModel):
    users: StatsCounter
    bot_users: StatsCounter
    events: StatsCounter
    top_products: list[StatsTopProduct]
    top_providers: list[StatsTopProvider]
    amount_buckets: list[StatsAmountBucket]
    amount_summary: StatsAmountSummary
    daily_activity: list[StatsDailyPoint]
    hourly_activity: list[StatsHourlyPoint]
    event_types: list[StatsEventTypeRow]
    languages: list[StatsEventTypeRow]
    funnel: list[StatsFunnelStep]
