"""Tiny dict-based i18n for the bot — UZ / RU / EN."""

from __future__ import annotations

from typing import Final, Literal

Lang = Literal["uz", "ru", "en"]

DEFAULT_LANG: Final[Lang] = "uz"
SUPPORTED: Final[tuple[Lang, ...]] = ("uz", "ru", "en")


_TRANSLATIONS: dict[str, dict[Lang, str]] = {
    # ─── /start ────────────────────────────────────────────────
    "welcome": {
        "uz": (
            "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            "Men — <b>Nasiya Aggregator</b> botiman.\n"
            "O'zbekistondagi barcha rasmiy nasiya xizmatlari (Alif, Uzum, IMAN, TBC, Anorbank…)\n"
            "limitlari, muddatlari va rasmiy linklarini bir joyda taqdim etaman.\n\n"
            "📌 Barcha ma'lumotlar — provayderlarning rasmiy manbalaridan."
        ),
        "ru": (
            "Здравствуйте, <b>{name}</b>! 👋\n\n"
            "Я — бот <b>Nasiya Aggregator</b>.\n"
            "Здесь вы найдёте все официальные сервисы рассрочки в Узбекистане "
            "(Alif, Uzum, IMAN, TBC, Anorbank…) — лимиты, сроки и официальные ссылки в одном месте.\n\n"
            "📌 Все данные — из официальных источников провайдеров."
        ),
        "en": (
            "Hello, <b>{name}</b>! 👋\n\n"
            "I'm the <b>Nasiya Aggregator</b> bot.\n"
            "I show you all official BNPL/installment services in Uzbekistan "
            "(Alif, Uzum, IMAN, TBC, Anorbank…) — limits, terms and official links in one place.\n\n"
            "📌 All data comes from each provider's official source."
        ),
    },
    # ─── Menu buttons ──────────────────────────────────────────
    "btn.all": {"uz": "📋 Barcha xizmatlar", "ru": "📋 Все сервисы", "en": "📋 All services"},
    "btn.search": {
        "uz": "🔍 Qancha summa kerak?",
        "ru": "🔍 Какая сумма нужна?",
        "en": "🔍 How much do you need?",
    },
    "btn.compare": {"uz": "📊 Solishtirish", "ru": "📊 Сравнение", "en": "📊 Compare"},
    "btn.lang": {"uz": "🌐 Til", "ru": "🌐 Язык", "en": "🌐 Language"},
    "btn.feedback": {
        "uz": "💬 Fikr-mulohaza",
        "ru": "💬 Обратная связь",
        "en": "💬 Feedback",
    },
    "btn.back": {"uz": "« Bosh menyu", "ru": "« Главное меню", "en": "« Main menu"},
    "btn.back_short": {"uz": "« Orqaga", "ru": "« Назад", "en": "« Back"},
    "btn.back_list": {
        "uz": "« Xizmatlar ro'yxatiga",
        "ru": "« К списку сервисов",
        "en": "« Back to list",
    },
    "badge.unverified": {
        "uz": "⚠ Limit tasdiqlanmagan",
        "ru": "⚠ Лимит не подтверждён",
        "en": "⚠ Limit not verified",
    },
    "btn.official_site": {
        "uz": "🌐 Rasmiy sayt",
        "ru": "🌐 Официальный сайт",
        "en": "🌐 Official website",
    },
    "btn.app_store": {"uz": "📱 App Store", "ru": "📱 App Store", "en": "📱 App Store"},
    "btn.play_store": {"uz": "🤖 Google Play", "ru": "🤖 Google Play", "en": "🤖 Google Play"},
    "btn.tg_bot": {
        "uz": "💬 Rasmiy bot",
        "ru": "💬 Официальный бот",
        "en": "💬 Official bot",
    },
    "btn.add_compare": {
        "uz": "➕ Solishtirishga qo'shish",
        "ru": "➕ Добавить к сравнению",
        "en": "➕ Add to compare",
    },
    "btn.show_compare": {
        "uz": "📊 Solishtirishni ko'rsatish ({n})",
        "ru": "📊 Показать сравнение ({n})",
        "en": "📊 Show comparison ({n})",
    },
    "btn.clear_compare": {
        "uz": "🗑 Tozalash",
        "ru": "🗑 Очистить",
        "en": "🗑 Clear",
    },
    # ─── List & search ─────────────────────────────────────────
    "list.title": {
        "uz": "O'zbekistondagi nasiya xizmatlari (<b>{n} ta</b>):",
        "ru": "Сервисы рассрочки в Узбекистане (<b>{n}</b>):",
        "en": "Installment services in Uzbekistan (<b>{n}</b>):",
    },
    "list.empty": {
        "uz": "Hozircha xizmatlar yo'q.",
        "ru": "Сервисов пока нет.",
        "en": "No services yet.",
    },
    "search.prompt": {
        "uz": "Kerakli summani <b>so'mda</b> yuboring (raqamlar bilan).\nMisol: <code>5000000</code>",
        "ru": "Отправьте нужную сумму <b>в сумах</b> (цифрами).\nПример: <code>5000000</code>",
        "en": "Send the amount you need <b>in UZS</b> (digits only).\nExample: <code>5000000</code>",
    },
    "search.none": {
        "uz": "<b>{amount}</b> uchun mos xizmat topilmadi.",
        "ru": "Подходящих сервисов для <b>{amount}</b> не найдено.",
        "en": "No matching services found for <b>{amount}</b>.",
    },
    "search.found": {
        "uz": "<b>{amount}</b> uchun mos: <b>{n} ta</b> xizmat:",
        "ru": "Подходит для <b>{amount}</b>: <b>{n}</b> сервис(ов):",
        "en": "Match for <b>{amount}</b>: <b>{n}</b> service(s):",
    },
    # ─── Product card ──────────────────────────────────────────
    "card.limit": {"uz": "💰 Limit:", "ru": "💰 Лимит:", "en": "💰 Limit:"},
    "card.term": {"uz": "📅 Muddat:", "ru": "📅 Срок:", "en": "📅 Term:"},
    "card.interest_free": {
        "uz": "✅ <b>Foizsiz</b> (rasmiy e'lon)",
        "ru": "✅ <b>Без процентов</b> (по официальным данным)",
        "en": "✅ <b>Interest-free</b> (per official statement)",
    },
    "card.age": {"uz": "👤 Yosh:", "ru": "👤 Возраст:", "en": "👤 Age:"},
    "card.phone": {"uz": "📞", "ru": "📞", "en": "📞"},
    "card.verified": {
        "uz": "<i>Ma'lumot rasmiy manbadan olingan.</i>",
        "ru": "<i>Данные взяты из официального источника.</i>",
        "en": "<i>Data is sourced from the official provider.</i>",
    },
    "card.term_unit": {"uz": "oy", "ru": "мес", "en": "mo"},
    # ─── Compare ──────────────────────────────────────────────
    "cmp.title": {
        "uz": "📊 Solishtirish ({n} ta xizmat):",
        "ru": "📊 Сравнение ({n} сервис(ов)):",
        "en": "📊 Comparison ({n} services):",
    },
    "cmp.added": {
        "uz": "✅ Solishtirishga qo'shildi ({n} ta)",
        "ru": "✅ Добавлено к сравнению ({n})",
        "en": "✅ Added to comparison ({n})",
    },
    "cmp.already": {
        "uz": "Allaqachon qo'shilgan.",
        "ru": "Уже добавлено.",
        "en": "Already added.",
    },
    "cmp.full": {
        "uz": "Maksimal 3 ta xizmat solishtiriladi.",
        "ru": "Максимум 3 сервиса.",
        "en": "Maximum 3 services.",
    },
    "cmp.empty": {
        "uz": "Solishtirish ro'yxati bo'sh. Xizmat kartochkasidan «Solishtirishga qo'shish» bosing.",
        "ru": "Список сравнения пуст. Нажмите «Добавить к сравнению» в карточке.",
        "en": "Compare list is empty. Tap «Add to compare» on a card.",
    },
    "cmp.cleared": {"uz": "Tozalandi.", "ru": "Очищено.", "en": "Cleared."},
    # ─── Language ─────────────────────────────────────────────
    "lang.choose": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Choose your language:",
    },
    "lang.set": {"uz": "Til o'zgartirildi.", "ru": "Язык изменён.", "en": "Language updated."},
    # ─── Feedback ─────────────────────────────────────────────
    "fb.prompt": {
        "uz": (
            "💬 Fikr-mulohazangizni yozing.\n\n"
            "Botga, xizmatlar ro'yxatiga yoki kerakli yangi funksiyalarga oid "
            "har qanday izoh — biz uchun qimmatli. (Bekor qilish uchun /cancel yuboring.)"
        ),
        "ru": (
            "💬 Напишите ваш отзыв.\n\n"
            "Любые комментарии о боте, списке сервисов или нужных функциях — "
            "для нас ценны. (Для отмены отправьте /cancel.)"
        ),
        "en": (
            "💬 Send us your feedback.\n\n"
            "Any comments about the bot, the services list, or features you'd like — "
            "we read every one. (Send /cancel to abort.)"
        ),
    },
    "fb.too_short": {
        "uz": "Iltimos, kamida 5 ta belgi yozing.",
        "ru": "Пожалуйста, напишите хотя бы 5 символов.",
        "en": "Please write at least 5 characters.",
    },
    "fb.thanks": {
        "uz": "✅ Rahmat! Fikringiz qabul qilindi.",
        "ru": "✅ Спасибо! Ваш отзыв получен.",
        "en": "✅ Thank you! Your feedback was received.",
    },
    "fb.cancelled": {
        "uz": "Bekor qilindi.",
        "ru": "Отменено.",
        "en": "Cancelled.",
    },
    # ─── Bot commands menu (shown via Telegram's "/" button) ──
    "cmd.start": {
        "uz": "Botni ishga tushirish",
        "ru": "Запустить бота",
        "en": "Start the bot",
    },
    "cmd.list": {
        "uz": "Barcha nasiya xizmatlari",
        "ru": "Все сервисы рассрочки",
        "en": "All installment services",
    },
    "cmd.search": {
        "uz": "Summa bo'yicha qidirish",
        "ru": "Поиск по сумме",
        "en": "Search by amount",
    },
    "cmd.compare": {
        "uz": "Solishtirishni ko'rsatish",
        "ru": "Показать сравнение",
        "en": "Show comparison",
    },
    "cmd.feedback": {
        "uz": "Fikr-mulohaza qoldirish",
        "ru": "Оставить отзыв",
        "en": "Leave feedback",
    },
    "cmd.lang": {
        "uz": "Tilni o'zgartirish",
        "ru": "Изменить язык",
        "en": "Change language",
    },
    "cmd.help": {
        "uz": "Yordam",
        "ru": "Помощь",
        "en": "Help",
    },
    # ─── /help text ───────────────────────────────────────────
    "help": {
        "uz": (
            "🤖 <b>Nasiya Aggregator</b>\n\n"
            "O'zbekistondagi barcha rasmiy nasiya xizmatlarini bir joyda taqdim etadi.\n\n"
            "<b>Komandalar:</b>\n"
            "/list — Barcha xizmatlar\n"
            "/search — Summa bo'yicha qidirish\n"
            "/compare — Solishtirish\n"
            "/feedback — Fikr-mulohaza\n"
            "/lang — Tilni o'zgartirish\n\n"
            "📌 Barcha ma'lumotlar provayderlarning rasmiy manbalaridan olingan."
        ),
        "ru": (
            "🤖 <b>Nasiya Aggregator</b>\n\n"
            "Все официальные сервисы рассрочки в Узбекистане в одном месте.\n\n"
            "<b>Команды:</b>\n"
            "/list — Все сервисы\n"
            "/search — Поиск по сумме\n"
            "/compare — Сравнение\n"
            "/feedback — Обратная связь\n"
            "/lang — Сменить язык\n\n"
            "📌 Все данные взяты из официальных источников провайдеров."
        ),
        "en": (
            "🤖 <b>Nasiya Aggregator</b>\n\n"
            "All official BNPL/installment services in Uzbekistan in one place.\n\n"
            "<b>Commands:</b>\n"
            "/list — All services\n"
            "/search — Search by amount\n"
            "/compare — Comparison\n"
            "/feedback — Send feedback\n"
            "/lang — Change language\n\n"
            "📌 All data comes from each provider's official source."
        ),
    },
    # ─── Misc ─────────────────────────────────────────────────
    "menu": {"uz": "Bosh menyu:", "ru": "Главное меню:", "en": "Main menu:"},
    "uzs": {"uz": "so'm", "ru": "сум", "en": "UZS"},
}


def t(key: str, lang: Lang = DEFAULT_LANG, **fmt: object) -> str:
    """Lookup a translation. Falls back to UZ then to the key itself."""
    bundle = _TRANSLATIONS.get(key, {})
    text = bundle.get(lang) or bundle.get(DEFAULT_LANG) or key
    if fmt:
        try:
            return text.format(**fmt)
        except (KeyError, IndexError):
            return text
    return text


class Translator:
    """Tiny callable bound to a user's language."""

    __slots__ = ("lang",)

    def __init__(self, lang: Lang) -> None:
        self.lang = lang

    def __call__(self, key: str, **fmt: object) -> str:
        return t(key, self.lang, **fmt)


def detect_lang(telegram_lang_code: str | None) -> Lang:
    """Map Telegram's language_code to one of our supported languages."""
    if not telegram_lang_code:
        return DEFAULT_LANG
    code = telegram_lang_code.lower()[:2]
    if code in {"ru", "kk", "ky"}:  # Russian + close Turkic users often pick Russian
        return "ru"
    if code == "en":
        return "en"
    return "uz"
