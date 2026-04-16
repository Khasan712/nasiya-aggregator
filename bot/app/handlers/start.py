"""/start and /help handlers."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.i18n import Translator
from app.keyboards.main import main_menu_kb
from app.services.events import track
from app.services.user_state import compare_count

router = Router()


@router.message(CommandStart())
async def on_start(message: Message, _: Translator) -> None:
    user = message.from_user
    name = user.first_name if user else "do'st"
    n = await compare_count(user.id) if user else 0
    track(user, "start", lang=_.lang)
    await message.answer(
        _("welcome", name=name),
        reply_markup=main_menu_kb(_, compare_count=n),
    )


@router.message(Command("help"))
async def on_help(message: Message, _: Translator) -> None:
    await message.answer(_("help"), disable_web_page_preview=True)
