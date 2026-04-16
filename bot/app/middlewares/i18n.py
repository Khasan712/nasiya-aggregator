"""Inject the current user's Translator (`_`) and language into every handler."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser

from app.i18n import DEFAULT_LANG, Translator
from app.services.user_state import get_lang


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user:
            lang = await get_lang(tg_user.id, tg_user.language_code)
        else:
            lang = DEFAULT_LANG
        data["lang"] = lang
        data["_"] = Translator(lang)
        return await handler(event, data)
