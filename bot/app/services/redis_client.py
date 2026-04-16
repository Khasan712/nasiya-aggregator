"""Shared Redis async client."""

from __future__ import annotations

import redis.asyncio as redis_async

from app.config import settings

redis: redis_async.Redis = redis_async.from_url(
    settings.redis_url,
    decode_responses=True,
)
