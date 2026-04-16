"""Feedback collection — single-step state in Redis (no FSM library needed)."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.i18n import Translator
from app.services.events import submit_feedback, track
from app.services.redis_client import redis

log = logging.getLogger(__name__)
router = Router()

# Redis key — true while we're waiting for the user's next message to be
# treated as feedback text. TTL 5 min (anti-stuck).
_AWAIT_KEY = "fb_await:{user_id}"
_AWAIT_TTL = 60 * 5


async def _is_awaiting(user_id: int) -> bool:
    return bool(await redis.get(_AWAIT_KEY.format(user_id=user_id)))


async def _set_awaiting(user_id: int, on: bool) -> None:
    key = _AWAIT_KEY.format(user_id=user_id)
    if on:
        await redis.set(key, "1", ex=_AWAIT_TTL)
    else:
        await redis.delete(key)


# ─── Entry: button or /feedback command ─────────────────────────────────────


@router.message(Command("feedback"))
@router.message(F.text.in_({"💬 Fikr-mulohaza", "💬 Обратная связь", "💬 Feedback"}))
async def ask_feedback(message: Message, _: Translator) -> None:
    await _set_awaiting(message.from_user.id, True)
    await message.answer(_("fb.prompt"))


@router.message(Command("cancel"))
async def cancel_feedback(message: Message, _: Translator) -> None:
    if await _is_awaiting(message.from_user.id):
        await _set_awaiting(message.from_user.id, False)
        await message.answer(_("fb.cancelled"))


# ─── Catch-all: only fires when the user is in the "awaiting feedback" state.
#
# This must be registered AFTER the more specific handlers (start/lang/all-services
# buttons / search amount / compare). The router include order in
# bot/app/handlers/__init__.py guarantees that — `feedback` is included last.
# ────────────────────────────────────────────────────────────────────────────


@router.message(F.text)
async def collect_feedback(message: Message, _: Translator) -> None:
    if not await _is_awaiting(message.from_user.id):
        return  # Not in feedback mode — let the dispatcher fall through

    text = (message.text or "").strip()
    if len(text) < 5:
        await message.answer(_("fb.too_short"))
        return

    ok = await submit_feedback(message.from_user, lang=_.lang, text=text)
    await _set_awaiting(message.from_user.id, False)
    track(
        message.from_user,
        "feedback",
        lang=_.lang,
        payload={"chars": len(text), "ok": ok},
    )
    if ok:
        await message.answer(_("fb.thanks"))
    else:
        await message.answer("⚠")
