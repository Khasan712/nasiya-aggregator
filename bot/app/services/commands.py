"""Register the bot's command menu (the / button) for each supported language.

Telegram lets us set per-language defaults via BotCommandScopeAllPrivateChats
+ language_code. The user's Telegram client picks whichever bundle matches
their UI language; we always set UZ as the unconditional fallback.
"""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.i18n import SUPPORTED, Lang, t

log = logging.getLogger(__name__)

# Order here = order in the Telegram menu.
COMMANDS: tuple[str, ...] = (
    "start",
    "list",
    "search",
    "compare",
    "feedback",
    "lang",
    "help",
)


def _commands_for(lang: Lang) -> list[BotCommand]:
    return [BotCommand(command=c, description=t(f"cmd.{c}", lang)) for c in COMMANDS]


async def setup_bot_commands(bot: Bot) -> None:
    # Default (no language_code) — Uzbek.
    await bot.set_my_commands(
        _commands_for("uz"),
        scope=BotCommandScopeAllPrivateChats(),
    )
    # Per-language overrides.
    for lang in SUPPORTED:
        await bot.set_my_commands(
            _commands_for(lang),
            scope=BotCommandScopeAllPrivateChats(),
            language_code=lang,
        )
    log.info("bot commands registered for %s", list(SUPPORTED))
