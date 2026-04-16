"""/lang command and language selection."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.i18n import SUPPORTED, Lang, Translator, t
from app.keyboards.main import lang_kb, main_menu_kb
from app.services.events import track
from app.services.user_state import compare_count, set_lang

router = Router()


@router.message(Command("lang"))
@router.message(F.text.in_({"🌐 Til", "🌐 Язык", "🌐 Language"}))
async def show_lang_picker(message: Message, _: Translator) -> None:
    await message.answer(_("lang.choose"), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("setlang:"))
async def on_set_lang(cb: CallbackQuery) -> None:
    new_lang = cb.data.split(":")[1]
    if new_lang not in SUPPORTED:
        await cb.answer("?")
        return
    lang: Lang = new_lang  # type: ignore[assignment]
    await set_lang(cb.from_user.id, lang)
    track(cb.from_user, "language_change", lang=lang, payload={"to": lang})

    fresh = Translator(lang)
    n = await compare_count(cb.from_user.id)
    await cb.message.answer(fresh("lang.set"), reply_markup=main_menu_kb(fresh, compare_count=n))
    await cb.answer(t("lang.set", lang))
