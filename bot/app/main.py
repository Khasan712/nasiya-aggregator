"""Bot entrypoint — long polling with i18n middleware."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.handlers import router as handlers_router
from app.middlewares.i18n import I18nMiddleware
from app.services.api_client import backend
from app.services.commands import setup_bot_commands
from app.services.events import aclose as events_close
from app.services.redis_client import redis


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log = logging.getLogger("bot")

    if not settings.bot_token:
        log.error("BOT_TOKEN is empty. Set it in .env (from @BotFather).")
        sys.exit(1)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # i18n must run early so every handler gets `_` and `lang`
    i18n = I18nMiddleware()
    dp.message.middleware(i18n)
    dp.callback_query.middleware(i18n)

    dp.include_router(handlers_router)

    # Register the "/" command menu in all 3 languages.
    try:
        await setup_bot_commands(bot)
    except Exception as exc:  # noqa: BLE001
        log.warning("setup_bot_commands failed (non-fatal): %s", exc)

    log.info("Bot starting (long polling) with i18n...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await backend.close()
        await events_close()
        await redis.aclose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
