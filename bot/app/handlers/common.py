"""Common handlers — list, search, product card, compare."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.i18n import Translator, t
from app.keyboards.main import (
    compare_view_kb,
    main_menu_kb,
    product_card_kb,
    products_list_kb,
)
from app.services.api_client import Product, backend
from app.services.events import track
from app.services.user_state import (
    compare_add,
    compare_clear,
    compare_count,
    compare_get,
    recall_list,
    remember_list,
)

log = logging.getLogger(__name__)
router = Router()


# ─── formatting helpers ────────────────────────────────────────────────────


def fmt_uzs(amount: int | None, lang: str) -> str:
    if amount is None:
        return "—"
    unit = t("uzs", lang)  # type: ignore[arg-type]
    return f"{amount:,}".replace(",", " ") + f" {unit}"


def fmt_terms(p: Product, lang: str) -> str:
    unit = t("card.term_unit", lang)  # type: ignore[arg-type]
    if p.allowed_terms:
        return " / ".join(f"{x} {unit}" for x in p.allowed_terms)
    if p.min_term_months and p.max_term_months:
        return f"{p.min_term_months}–{p.max_term_months} {unit}"
    if p.max_term_months:
        return f"{p.max_term_months} {unit}"
    return "—"


def render_card(p: Product, _: Translator) -> str:
    lines: list[str] = [f"<b>{p.name_uz}</b>", ""]
    if p.status == "needs_verification":
        lines.append(_("badge.unverified"))
        lines.append("")
    lines.append(
        f"{_('card.limit')} <b>"
        f"{fmt_uzs(p.min_limit_uzs, _.lang) if p.min_limit_uzs else '—'} – "
        f"{fmt_uzs(p.max_limit_uzs, _.lang)}</b>"
    )
    lines.append(f"{_('card.term')} <b>{fmt_terms(p, _.lang)}</b>")
    if p.is_interest_free:
        lines.append(_("card.interest_free"))
    elif p.markup_note_uz:
        lines.append(f"💼 {p.markup_note_uz}")
    if p.min_age and p.max_age:
        lines.append(f"{_('card.age')} <b>{p.min_age}–{p.max_age}</b>")
    if p.support_phone:
        lines.append(f"{_('card.phone')} {p.support_phone}")
    if p.status != "needs_verification":
        lines.append("")
        lines.append(_("card.verified"))
    return "\n".join(lines)


async def _safe_edit(cb: CallbackQuery, text: str, **kwargs) -> None:
    """edit_text that swallows the 'message is not modified' error."""
    try:
        await cb.message.edit_text(text, **kwargs)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        log.warning("edit_text failed, falling back to answer: %s", exc)
        await cb.message.answer(text, **kwargs)


# ─── List ──────────────────────────────────────────────────────────────────


@router.message(Command("list"))
@router.message(F.text.in_({"📋 Barcha xizmatlar", "📋 Все сервисы", "📋 All services"}))
async def list_all(message: Message, _: Translator) -> None:
    track(message.from_user, "view_list", lang=_.lang)
    products = await backend.list_products()
    await remember_list(message.from_user.id, "all")
    if not products:
        await message.answer(_("list.empty"))
        return
    await message.answer(
        _("list.title", n=len(products)),
        reply_markup=products_list_kb(products, _),
    )


# ─── Search by amount ─────────────────────────────────────────────────────


@router.message(Command("search"))
@router.message(F.text.in_({"🔍 Qancha summa kerak?", "🔍 Какая сумма нужна?", "🔍 How much do you need?"}))
async def ask_amount(message: Message, _: Translator) -> None:
    await message.answer(_("search.prompt"))


@router.message(F.text.regexp(r"^\d{4,12}$"))
async def search_by_amount(message: Message, _: Translator) -> None:
    amount = int(message.text)
    track(message.from_user, "search_by_amount", lang=_.lang, payload={"amount": amount})
    products = await backend.list_products(amount_uzs=amount)
    await remember_list(message.from_user.id, "search", amount=amount)
    if not products:
        await message.answer(_("search.none", amount=fmt_uzs(amount, _.lang)))
        return
    await message.answer(
        _("search.found", amount=fmt_uzs(amount, _.lang), n=len(products)),
        reply_markup=products_list_kb(products, _),
    )


# ─── Product card ─────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("p:"))
async def show_product(cb: CallbackQuery, _: Translator) -> None:
    product_id = int(cb.data.split(":")[1])
    track(cb.from_user, "view_product", lang=_.lang, product_id=product_id)
    p = await backend.get_product(product_id)
    # Edit the list message in place so we don't flood the chat with new messages.
    await _safe_edit(
        cb,
        render_card(p, _),
        reply_markup=product_card_kb(p, _),
        disable_web_page_preview=True,
    )
    await cb.answer()


# ─── Back from card → list (edit same message) ────────────────────────────


@router.callback_query(F.data == "back:list")
async def back_to_list(cb: CallbackQuery, _: Translator) -> None:
    kind, amount = await recall_list(cb.from_user.id)
    if kind == "search" and amount:
        products = await backend.list_products(amount_uzs=amount)
        title = _("search.found", amount=fmt_uzs(amount, _.lang), n=len(products))
    else:
        products = await backend.list_products()
        title = _("list.title", n=len(products))
    if not products:
        await _safe_edit(cb, _("list.empty"))
        await cb.answer()
        return
    await _safe_edit(cb, title, reply_markup=products_list_kb(products, _))
    await cb.answer()


# ─── Compare ──────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("cmp:add:"))
async def cmp_add(cb: CallbackQuery, _: Translator) -> None:
    """Add a product to the compare list. We deliberately do NOT touch the
    ReplyKeyboardMarkup here: deleting a temp message that we'd send to refresh
    it can wipe the keyboard for the user (observed: bottom keyboard disappears
    after Telegram garbage-collects the deleted message). Instead, the new
    count is shown in the toast, and the next time the user sends any reply-
    keyboard text the menu will naturally refresh with the updated counter.
    """
    product_id = int(cb.data.split(":")[2])
    _ok, status = await compare_add(cb.from_user.id, product_id)
    if status == "added":
        n = await compare_count(cb.from_user.id)
        await cb.answer(_("cmp.added", n=n), show_alert=False)
    elif status == "already":
        await cb.answer(_("cmp.already"), show_alert=False)
    elif status == "full":
        await cb.answer(_("cmp.full"), show_alert=True)


@router.message(Command("compare"))
@router.message(F.text.regexp(r"^📊 (Solishtirish|Сравнение|Compare).*"))
@router.message(F.text.regexp(r"^📊 (Solishtirishni|Показать|Show).*"))
async def show_compare(message: Message, _: Translator) -> None:
    ids = await compare_get(message.from_user.id)
    if not ids:
        await message.answer(_("cmp.empty"))
        return
    track(message.from_user, "compare", lang=_.lang, payload={"product_ids": ids})
    products: list[Product] = []
    for pid in ids:
        try:
            products.append(await backend.get_product(pid))
        except Exception:
            continue
    if not products:
        await compare_clear(message.from_user.id)
        await message.answer(_("cmp.empty"))
        return

    blocks = [_("cmp.title", n=len(products)), ""]
    for p in products:
        blocks.append(render_card(p, _))
        blocks.append("─" * 20)
    blocks.pop()  # remove last separator

    await message.answer(
        "\n".join(blocks), reply_markup=compare_view_kb(_), disable_web_page_preview=True
    )


@router.callback_query(F.data == "cmp:clear")
async def cmp_clear(cb: CallbackQuery, _: Translator) -> None:
    await compare_clear(cb.from_user.id)
    await _safe_edit(cb, _("cmp.empty"))
    await cb.answer(_("cmp.cleared"))
    # Refresh the reply keyboard with the now-zero counter. This is safe
    # because we keep this message in the chat (compare clear is a meaningful
    # action — no need to hide the confirmation).
    await cb.message.answer(_("menu"), reply_markup=main_menu_kb(_, compare_count=0))


# ─── Back to main menu (legacy — only reachable from compare view) ────────


@router.callback_query(F.data == "back:menu")
async def back_to_menu(cb: CallbackQuery, _: Translator) -> None:
    n = await compare_count(cb.from_user.id)
    await cb.message.answer(_("menu"), reply_markup=main_menu_kb(_, compare_count=n))
    await cb.answer()
