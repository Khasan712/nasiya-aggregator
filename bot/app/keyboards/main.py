"""Reply + inline keyboards (i18n-aware)."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.i18n import Translator
from app.services.api_client import Product


def main_menu_kb(_: Translator, compare_count: int = 0) -> ReplyKeyboardMarkup:
    cmp_label = (
        _("btn.show_compare", n=compare_count) if compare_count else _("btn.compare")
    )
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("btn.all"))],
            [KeyboardButton(text=cmp_label), KeyboardButton(text=_("btn.search"))],
            [KeyboardButton(text=_("btn.lang")), KeyboardButton(text=_("btn.feedback"))],
        ],
        resize_keyboard=True,
    )


def back_kb(_: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_("btn.back"), callback_data="back:menu")]]
    )


def products_list_kb(products: list[Product], _: Translator) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for p in products:
        if p.max_limit_uzs:
            suffix = f" — {p.max_limit_uzs // 1_000_000} mln"
        elif p.status == "needs_verification":
            suffix = " ⚠"
        else:
            suffix = ""
        rows.append(
            [InlineKeyboardButton(text=f"{p.name_uz}{suffix}", callback_data=f"p:{p.id}")]
        )
    # No "back to menu" button — the reply keyboard at the bottom of the chat
    # already gives access to the main menu at any time.
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card_kb(p: Product, _: Translator) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if p.official_url:
        rows.append([InlineKeyboardButton(text=_("btn.official_site"), url=p.official_url)])
    pair: list[InlineKeyboardButton] = []
    if p.ios_app_url:
        pair.append(InlineKeyboardButton(text=_("btn.app_store"), url=p.ios_app_url))
    if p.android_app_url:
        pair.append(InlineKeyboardButton(text=_("btn.play_store"), url=p.android_app_url))
    if pair:
        rows.append(pair)
    if p.telegram_bot:
        bot_username = p.telegram_bot.lstrip("@")
        rows.append(
            [InlineKeyboardButton(text=_("btn.tg_bot"), url=f"https://t.me/{bot_username}")]
        )
    rows.append(
        [InlineKeyboardButton(text=_("btn.add_compare"), callback_data=f"cmp:add:{p.id}")]
    )
    # Back returns to the product list (edits the same message).
    rows.append([InlineKeyboardButton(text=_("btn.back_list"), callback_data="back:list")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang:en"),
            ]
        ]
    )


def compare_view_kb(_: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("btn.clear_compare"), callback_data="cmp:clear")],
            [InlineKeyboardButton(text=_("btn.back"), callback_data="back:menu")],
        ]
    )
