"""Send admin notifications via Telegram Bot API (used by scheduled jobs)."""

from __future__ import annotations

import logging
from typing import Iterable

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)


async def notify_admins(text: str) -> None:
    """Send a Telegram HTML message to every BOT_ADMIN_IDS user. Silent on failure."""
    if not settings.bot_token or not settings.bot_admin_ids:
        log.info("notify_admins skipped — no bot_token or admin ids configured")
        return
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        for admin_id in settings.bot_admin_ids:
            try:
                r = await client.post(
                    url,
                    json={
                        "chat_id": admin_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                )
                if r.status_code >= 400:
                    log.warning("notify failed for %s: %s %s", admin_id, r.status_code, r.text[:200])
            except Exception as exc:  # noqa: BLE001
                log.warning("notify exception for %s: %s", admin_id, exc)
