"""Fire-and-forget event tracking — bot → backend.

Events are posted asynchronously; failures are logged but never raised so
the user-facing handler is never blocked or broken by analytics.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from aiogram.types import User as TgUser

from app.config import settings
from app.i18n import Lang

log = logging.getLogger(__name__)

_client = httpx.AsyncClient(base_url=settings.backend_url, timeout=5.0)


async def _send(body: dict[str, Any]) -> None:
    if not settings.service_token:
        return
    try:
        r = await _client.post(
            "/api/v1/bot/events",
            json=body,
            headers={"X-Service-Token": settings.service_token},
        )
        if r.status_code >= 400:
            log.warning("track failed %s: %s %s", body.get("event_type"), r.status_code, r.text[:120])
    except Exception as exc:  # noqa: BLE001
        log.warning("track exception %s: %s", body.get("event_type"), exc)


def track(
    user: TgUser | None,
    event_type: str,
    *,
    lang: Lang | None = None,
    product_id: int | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Schedule a tracking call — returns immediately."""
    if user is None:
        return
    body: dict[str, Any] = {
        "telegram_id": user.id,
        "event_type": event_type,
    }
    if user.username:
        body["telegram_username"] = user.username
    if user.first_name:
        body["first_name"] = user.first_name
    if user.last_name:
        body["last_name"] = user.last_name
    if lang:
        body["language"] = lang
    if product_id is not None:
        body["product_id"] = product_id
    if payload is not None:
        body["payload"] = payload
    # Fire and forget
    asyncio.create_task(_send(body))


async def submit_feedback(user, *, lang: Lang, text: str) -> bool:
    """POST to /api/v1/bot/feedback. Returns True on success."""
    if not settings.service_token:
        log.warning("feedback skipped — no service_token")
        return False
    body: dict[str, Any] = {
        "telegram_id": user.id,
        "language": lang,
        "text": text,
    }
    if user.username:
        body["telegram_username"] = user.username
    if user.first_name:
        body["first_name"] = user.first_name
    if user.last_name:
        body["last_name"] = user.last_name
    try:
        r = await _client.post(
            "/api/v1/bot/feedback",
            json=body,
            headers={"X-Service-Token": settings.service_token},
        )
        return r.status_code < 400
    except Exception as exc:  # noqa: BLE001
        log.warning("feedback exception: %s", exc)
        return False


async def aclose() -> None:
    await _client.aclose()
