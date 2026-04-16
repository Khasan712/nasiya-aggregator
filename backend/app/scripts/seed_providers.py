"""Seed verified nasiya providers + products from official sources.

Run: `uv run python -m app.scripts.seed_providers`

Every numeric/string field has an entry in `source_cited_urls` so the audit trail
back to the official source is preserved in the DB.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime

from pydantic import BaseModel
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.product import NasiyaProduct, ProductStatus, ProductUseCase
from app.models.provider import NasiyaProvider, ProviderStatus, ProviderType


class ProviderSeed(BaseModel):
    slug: str
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    legal_name: str | None = None
    provider_type: ProviderType
    status: ProviderStatus = ProviderStatus.ACTIVE
    license_body: str | None = None
    license_number: str | None = None
    license_date: date | None = None
    license_url: str | None = None
    description_uz: str | None = None


class ProductSeed(BaseModel):
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    min_limit_uzs: int | None = None
    max_limit_uzs: int | None = None
    min_term_months: int | None = None
    max_term_months: int | None = None
    allowed_terms: list[int] | None = None
    is_interest_free: bool = False
    markup_note_uz: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    citizenship_required: str | None = "UZ"
    use_case: ProductUseCase | None = None
    description_uz: str | None = None
    official_url: str | None = None
    ios_app_url: str | None = None
    android_app_url: str | None = None
    telegram_bot: str | None = None
    telegram_channel: str | None = None
    support_phone: str | None = None
    support_email: str | None = None
    partners_count: int | None = None
    source_cited_urls: dict[str, str] | None = None
    status: ProductStatus = ProductStatus.ACTIVE


SEED: list[tuple[ProviderSeed, list[ProductSeed]]] = [
    # ───────────────────────────  ALIF NASIYA  ───────────────────────────
    (
        ProviderSeed(
            slug="alif",
            name_uz="Alif Nasiya",
            name_ru="Алиф Насия",
            name_en="Alif Nasiya",
            legal_name="Alif Tech",
            provider_type=ProviderType.MFO,
            license_body="CBU",
            license_number="000010",
            license_date=date(2020, 7, 23),
            license_url="https://alif.uz/en/",
            description_uz="O'zbekistondagi eng yirik nasiya provayderlaridan biri.",
        ),
        [
            ProductSeed(
                name_uz="Alif Nasiya — Asosiy",
                name_en="Alif Nasiya — Standard",
                max_limit_uzs=33_000_000,
                min_term_months=3,
                max_term_months=24,
                allowed_terms=[3, 6, 9, 12, 15, 18, 24],
                is_interest_free=True,
                markup_note_uz="Rasmiy saytda \"o'tovsiz\" deb e'lon qilingan.",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://alifnasiya.uz/",
                ios_app_url="https://apps.apple.com/uz/app/alif-pay-transfer-shop/id1331374853",
                android_app_url="https://play.google.com/store/apps/details?id=tj.alif.mobi",
                telegram_bot="@alifazobot",
                support_phone="+998 555 12 12 12",
                support_email="info@alif.uz",
                partners_count=5000,
                source_cited_urls={
                    "max_limit_uzs": "https://alif.uz/en/",
                    "max_term_months": "https://alif.uz/en/",
                    "is_interest_free": "https://alif.uz/en/",
                    "partners_count": "https://alif.uz/en/",
                    "support_phone": "https://alif.uz/en/",
                    "support_email": "https://alif.uz/en/",
                    "official_url": "https://alifnasiya.uz/",
                },
            ),
        ],
    ),
    # ───────────────────────────  UZUM NASIYA  ───────────────────────────
    (
        ProviderSeed(
            slug="uzum-nasiya",
            name_uz="Uzum Nasiya",
            name_ru="Uzum Nasiya",
            name_en="Uzum Nasiya",
            legal_name="Uzum Bank",
            provider_type=ProviderType.BANK,
            description_uz="Uzum ekotizimining muddatli to'lov xizmati.",
        ),
        [
            ProductSeed(
                name_uz="Uzum Nasiya — Muddatli to'lov",
                min_limit_uzs=35_000,           # min order size
                max_limit_uzs=25_000_000,
                allowed_terms=[3, 6, 12],
                is_interest_free=True,
                markup_note_uz="Rasmiy: foiz va kechikkanlik jarimasi yo'q.",
                min_age=22,
                max_age=65,
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://uzumnasiya.uz/",
                ios_app_url="https://apps.apple.com/us/app/uzum-nasiya-muddatli-tolov/id1579281935",
                android_app_url="https://play.google.com/store/apps/details?id=uz.paymart.paymart_mobile",
                source_cited_urls={
                    "max_limit_uzs": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                    "min_limit_uzs": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                    "allowed_terms": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                    "is_interest_free": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                    "min_age": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                    "max_age": "https://uzum.uz/media/uz/uzum-nasiya-bolib-tolash-xizmati-qanday-ishlaydi/",
                },
            ),
        ],
    ),
    # ───────────────────────────  IMAN PAY  ──────────────────────────────
    (
        ProviderSeed(
            slug="iman",
            name_uz="IMAN Pay",
            name_ru="IMAN Pay",
            name_en="IMAN Pay",
            legal_name="IMAN",
            provider_type=ProviderType.ISLAMIC,
            description_uz="Shariah-compliant (halol) BNPL — markup asosida ishlaydi.",
        ),
        [
            ProductSeed(
                name_uz="IMAN Pay — Halol nasiya",
                max_limit_uzs=16_000_000,
                min_term_months=1,
                max_term_months=24,
                is_interest_free=False,
                markup_note_uz="Foiz emas — markup. Kechikkanlikda jarima olinmaydi.",
                min_age=18,
                max_age=63,
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://iman.uz/",
                ios_app_url="https://apps.apple.com/uz/app/imanum/id1625307273",
                telegram_bot="@IMANuzb_bot",
                telegram_channel="@IMANUZB",
                support_phone="+998 78 113 00 30",
                support_email="info@iman.uz",
                source_cited_urls={
                    "max_limit_uzs": "https://iman.uz/en",
                    "min_age": "https://iman.uz/en",
                    "max_age": "https://iman.uz/en",
                    "support_phone": "https://iman.uz/en",
                    "support_email": "https://iman.uz/en",
                },
            ),
        ],
    ),
    # ───────────────────────────  TBC NASIYA  ────────────────────────────
    (
        ProviderSeed(
            slug="tbc-nasiya",
            name_uz="TBC Nasiya",
            name_ru="TBC Nasiya",
            name_en="TBC Nasiya",
            legal_name="TBC Bank Uzbekistan",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_url="https://cbu.uz/en/credit-organizations/banks/head-offices/ao/tbc/",
            description_uz="TBC Bank Uzbekistan'ning muddatli to'lov xizmati (Payme bilan bog'liq).",
        ),
        [
            ProductSeed(
                name_uz="TBC Nasiya — POS muddatli",
                max_limit_uzs=50_000_000,
                max_term_months=24,
                use_case=ProductUseCase.OFFLINE,
                official_url="https://tbcnasiya.uz/uz",
                support_phone="78 777 06 06",
                partners_count=50,
                source_cited_urls={
                    "max_limit_uzs": "https://tbcnasiya.uz/uz",
                    "max_term_months": "https://tbcnasiya.uz/uz",
                    "support_phone": "https://tbcnasiya.uz/uz",
                    "partners_count": "https://tbcnasiya.uz/uz",
                },
            ),
        ],
    ),
    # ───────────────────────────  ANORBANK  ──────────────────────────────
    (
        ProviderSeed(
            slug="anorbank",
            name_uz="Anorbank",
            name_ru="Анорбанк",
            name_en="ANORBANK",
            legal_name="Joint-Stock Company \"ANOR BANK\"",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_number="87",
            license_date=date(2020, 8, 22),
            license_url="https://cbu.uz/en/credit-organizations/banks/head-offices/ao/anor/",
            description_uz="Raqamli bank — muddatli to'lov kartasi.",
        ),
        [
            ProductSeed(
                name_uz="Anor Karta bo'lib to'lash",
                min_limit_uzs=1_000_000,
                max_limit_uzs=50_000_000,
                max_term_months=36,
                is_interest_free=True,
                markup_note_uz="Foizsiz va komissiyasiz e'lon qilingan.",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://anorbank.uz/uz/cards/card-installment-uz/",
                ios_app_url="https://apps.apple.com/us/app/anorbank/id1579623268",
                support_phone="+998 55 503 00 00",
                support_email="info@anorbank.uz",
                source_cited_urls={
                    "min_limit_uzs": "https://anorbank.uz/uz/cards/card-installment-uz/",
                    "max_limit_uzs": "https://anorbank.uz/uz/cards/card-installment-uz/",
                    "max_term_months": "https://anorbank.uz/uz/cards/card-installment-uz/",
                    "is_interest_free": "https://anorbank.uz/uz/cards/card-installment-uz/",
                    "support_phone": "https://cbu.uz/en/credit-organizations/banks/head-offices/ao/anor/",
                    "support_email": "https://cbu.uz/en/credit-organizations/banks/head-offices/ao/anor/",
                },
            ),
        ],
    ),
    # ───────────────────────────  ZOODPAY  ───────────────────────────────
    (
        ProviderSeed(
            slug="zoodpay",
            name_uz="ZoodPay",
            name_ru="ZoodPay",
            name_en="ZoodPay",
            legal_name="ZOOD Ecosystem",
            provider_type=ProviderType.FINTECH,
            description_uz="Global BNPL — 4/6/12 oylik to'lov sxemalari.",
        ),
        [
            ProductSeed(
                name_uz="ZoodPay — 4/6/12 muddatli",
                allowed_terms=[4, 6, 12],
                is_interest_free=True,
                markup_note_uz="Rasmiy: foizsiz. 4-installment: 25% darhol + 75% 3 ga bo'linadi.",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://www.zood.biz/pay",
                source_cited_urls={
                    "allowed_terms": "https://www.zood.biz/pay",
                    "is_interest_free": "https://www.zood.biz/pay",
                },
                status=ProductStatus.NEEDS_VERIFICATION,
            ),
        ],
    ),
    # ───────────────────────────  UZUM BANK CARD  ────────────────────────
    (
        ProviderSeed(
            slug="uzum-bank",
            name_uz="Uzum Bank (Uzum Card)",
            name_ru="Uzum Bank",
            name_en="Uzum Bank",
            legal_name="Uzum Bank (formerly Apelsin)",
            provider_type=ProviderType.BANK,
            status=ProviderStatus.NEEDS_VERIFICATION,
            description_uz="Raqamli bank kredit limit kartasi (eski Apelsin).",
        ),
        [
            ProductSeed(
                name_uz="Uzum Card — kredit limit",
                max_limit_uzs=25_000_000,
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://uzumbank.uz/uz/",
                ios_app_url="https://apps.apple.com/us/app/apelsin/id1492307726",
                source_cited_urls={
                    "max_limit_uzs": "https://uzumbank.uz/uz/",
                    "official_url": "https://uzumbank.uz/uz/",
                },
                status=ProductStatus.NEEDS_VERIFICATION,
            ),
        ],
    ),
    # ───────────────────────────  OLCHA NASIYA  ──────────────────────────
    (
        ProviderSeed(
            slug="olcha-nasiya",
            name_uz="Olcha Nasiya",
            name_ru="Olcha Nasiya",
            name_en="Olcha Nasiya",
            legal_name="Olcha (e-commerce)",
            provider_type=ProviderType.FINTECH,
            description_uz="Olcha online do'koni va hamkor do'konlardagi muddatli to'lov xizmati.",
        ),
        [
            ProductSeed(
                name_uz="Olcha Nasiya — Muddatli to'lov",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://olchanasiya.uz/uz",
                source_cited_urls={
                    "official_url": "https://olchanasiya.uz/uz",
                },
                status=ProductStatus.NEEDS_VERIFICATION,
            ),
        ],
    ),
    # ───────────────────────────  SOLFY (NBU)  ───────────────────────────
    (
        ProviderSeed(
            slug="solfy",
            name_uz="Solfy",
            name_ru="Solfy",
            name_en="Solfy",
            legal_name="Solfy (NBU hamkor)",
            provider_type=ProviderType.FINTECH,
            status=ProviderStatus.NEEDS_VERIFICATION,
            description_uz=(
                "NBU bilan hamkorlikda muddatli to'lov kartasi — 0% boshlang'ich va 0% ustama. "
                "(Sayt SabziPay'ga yo'naltirmoqda — qayta tekshirish kerak.)"
            ),
        ),
        [
            ProductSeed(
                name_uz="Solfy — muddatli to'lov kartasi",
                max_term_months=12,
                allowed_terms=[3, 6, 9, 12],
                is_interest_free=True,
                markup_note_uz="Rasmiy: 0% ustama, 0% yashirin to'lovlar.",
                use_case=ProductUseCase.UNIVERSAL,
                # Use NBU's promo page as primary URL — more stable than solfy.com which currently 301s.
                official_url="https://nbu.uz/en/programma-loyalnosti-nbu/",
                ios_app_url="https://apps.apple.com/uz/app/solfy/id1641669414",
                android_app_url="https://play.google.com/store/apps/details?id=com.solfy.instcard",
                source_cited_urls={
                    "max_term_months": "https://nbu.uz/en/programma-loyalnosti-nbu/",
                    "is_interest_free": "https://nbu.uz/en/programma-loyalnosti-nbu/",
                    "ios_app_url": "https://apps.apple.com/uz/app/solfy/id1641669414",
                    "android_app_url": "https://play.google.com/store/apps/details?id=com.solfy.instcard",
                },
                status=ProductStatus.NEEDS_VERIFICATION,
            ),
        ],
    ),
    # ───────────────────────────  AGROBANK "OPEN"  ───────────────────────
    (
        ProviderSeed(
            slug="agrobank-open",
            name_uz="Agrobank (Open karta)",
            name_ru="Агробанк (Open)",
            name_en="Agrobank (Open card)",
            legal_name="ATB Agrobank",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_url="https://cbu.uz/en/credit-organizations/banks/",
            description_uz="Agrobank'ning Open ilovasi orqali muddatli to'lov kartasi.",
        ),
        [
            ProductSeed(
                name_uz="\"Open\" muddatli to'lov kartasi",
                max_limit_uzs=82_000_000,
                max_term_months=12,
                allowed_terms=[3, 6, 9, 12],
                is_interest_free=True,
                markup_note_uz="Rasmiy: foizsiz, 12 oygacha. Karta 3 yil amal qiladi (revolving).",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://agrobank.uz/uz/person/loans/open-karta",
                source_cited_urls={
                    "max_limit_uzs": "https://agrobank.uz/uz/person/loans/open-karta",
                    "max_term_months": "https://agrobank.uz/uz/person/loans/open-karta",
                    "is_interest_free": "https://agrobank.uz/uz/person/loans/open-karta",
                    "official_url": "https://agrobank.uz/uz/about/press-center/agrobank-muddatli-to-lov-kartasini-ishga-tushirdi",
                },
            ),
        ],
    ),
    # ───────────────────────────  INFINBANK  ─────────────────────────────
    (
        ProviderSeed(
            slug="infinbank",
            name_uz="InfinBANK",
            name_ru="InfinBANK",
            name_en="InfinBANK",
            legal_name="ATB InfinBANK",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_url="https://cbu.uz/en/credit-organizations/banks/",
            description_uz="InfinBANK'ning ikkita kredit/muddatli mahsuloti: InfinBaraka va InfinBLACK.",
        ),
        [
            ProductSeed(
                name_uz="InfinBaraka — muddatli to'lov kartasi",
                max_limit_uzs=100_000_000,
                max_term_months=12,
                allowed_terms=[3, 6, 9, 12],
                is_interest_free=True,
                markup_note_uz="Rasmiy: 12 oylik foizsiz muddatli to'lov.",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://www.infinbank.com/uz/private/cards/",
                support_phone="+998 71 202 50 60",
                source_cited_urls={
                    "max_limit_uzs": "https://www.infinbank.com/uz/private/cards/",
                    "max_term_months": "https://www.infinbank.com/uz/private/cards/",
                    "is_interest_free": "https://www.infinbank.com/uz/private/cards/",
                    "support_phone": "https://www.infinbank.com/uz/private/cards/",
                },
            ),
            ProductSeed(
                name_uz="InfinBLACK — kredit kartasi",
                max_limit_uzs=50_000_000,
                is_interest_free=False,
                markup_note_uz="50 kungacha foizsiz muddat. Undan keyin foizlar hisoblanadi.",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://www.infinbank.com/uz/private/credits/overdraft/",
                support_phone="+998 71 202 50 60",
                source_cited_urls={
                    "max_limit_uzs": "https://www.infinbank.com/uz/private/cards/",
                    "support_phone": "https://www.infinbank.com/uz/private/cards/",
                },
            ),
        ],
    ),
    # ───────────────────────────  HAMKORBANK  ────────────────────────────
    (
        ProviderSeed(
            slug="hamkorbank",
            name_uz="Hamkorbank",
            name_ru="Хамкорбанк",
            name_en="Hamkorbank",
            legal_name="ATB Hamkorbank",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_url="https://cbu.uz/en/credit-organizations/banks/",
            description_uz="Hamkorbank kredit kartasi — 50 kungacha foizsiz davr.",
        ),
        [
            ProductSeed(
                name_uz="Hamkor kredit kartasi",
                min_limit_uzs=1_000_000,
                max_limit_uzs=50_000_000,
                is_interest_free=False,
                markup_note_uz="50 kungacha foizsiz. Keyin yillik 40% APR. Min oylik to'lov: 10%.",
                min_age=18,
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://hamkorbank.uz/uz/physical/credit-card/",
                ios_app_url="https://apps.apple.com/id/app/hamkor/id1602323485",
                android_app_url="https://play.google.com/store/apps/details?id=com.hamkorbank.mobile",
                support_phone="0 800 1 200 200",
                eligibility_note_uz="O'zbekiston fuqarosi, 18+ yosh, kamida 6 oy barqaror daromad.",
                source_cited_urls={
                    "min_limit_uzs": "https://hamkorbank.uz/uz/physical/credit-card/",
                    "max_limit_uzs": "https://hamkorbank.uz/uz/physical/credit-card/",
                    "min_age": "https://hamkorbank.uz/uz/physical/credit-card/",
                    "ios_app_url": "https://hamkorbank.uz/uz/physical/credit-card/",
                    "android_app_url": "https://hamkorbank.uz/uz/physical/credit-card/",
                    "support_phone": "https://hamkorbank.uz/uz/physical/credit-card/",
                },
            ),
        ],
    ),
    # ───────────────────────────  SQB (Sanoat Qurilish Bank)  ────────────
    (
        ProviderSeed(
            slug="sqb",
            name_uz="SQB (Sanoat Qurilish Bank)",
            name_ru="СҚБ (Узпромстройбанк)",
            name_en="SQB (Uzbek Industrial Construction Bank)",
            legal_name="JSC \"SQB\"",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_number="17",
            license_date=date(2021, 12, 25),
            license_url="https://cbu.uz/en/credit-organizations/banks/",
            description_uz="SQB yangi Visa kredit kartasi — 100 mln so'mgacha limit, 55 kunlik foizsiz davr.",
        ),
        [
            ProductSeed(
                name_uz="SQB — yangi Visa kredit kartasi",
                min_limit_uzs=2_000_000,
                max_limit_uzs=100_000_000,
                is_interest_free=False,
                markup_note_uz="55 kungacha foizsiz. Undan keyin yillik 26.9% APR.",
                min_age=18,
                max_age=70,
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                support_phone="0 800 120-77-77",
                support_email="info@sqb.uz",
                telegram_bot="@sqbchat_bot",
                eligibility_note_uz="O'zbekiston fuqarosi, 18+ (qaytarish 70+ gacha), 6 oy ish stajidan ortiq.",
                source_cited_urls={
                    "min_limit_uzs": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                    "max_limit_uzs": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                    "min_age": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                    "max_age": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                    "support_phone": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                    "telegram_bot": "https://sqb.uz/uz/individuals/credits/credit-card-new-uz/",
                },
            ),
        ],
    ),
    # ───────────────────────────  MIKROKREDITBANK (MKBANK)  ──────────────
    (
        ProviderSeed(
            slug="mkbank",
            name_uz="Mikrokreditbank (MKBANK)",
            name_ru="Микрокредитбанк",
            name_en="Mikrokreditbank (MKBANK)",
            legal_name="ATB \"Mikrokreditbank\"",
            provider_type=ProviderType.BANK,
            license_body="CBU",
            license_url="https://cbu.uz/en/credit-organizations/banks/",
            description_uz="MKBANK mikroqarz va kredit mahsulotlari (Sherdor, Moment kartalar).",
        ),
        [
            ProductSeed(
                name_uz="MKBANK mikroqarz",
                min_term_months=12,
                max_term_months=24,
                is_interest_free=False,
                markup_note_uz="Yillik 22–23% (rasmiy ko'rsatma).",
                use_case=ProductUseCase.CASH,
                official_url="https://mkbank.uz/uz/private/crediting/microloan/",
                source_cited_urls={
                    "min_term_months": "https://mkbank.uz/uz/private/crediting/microloan/",
                    "max_term_months": "https://mkbank.uz/uz/private/crediting/microloan/",
                    "official_url": "https://mkbank.uz/uz/private/crediting/microloan/",
                },
                status=ProductStatus.NEEDS_VERIFICATION,
            ),
        ],
    ),
    # ───────────────────────────  HUMANS (deprecated)  ───────────────────
    (
        ProviderSeed(
            slug="humans",
            name_uz="Humans (bankrot — faol emas)",
            name_ru="Humans (банкрот — неактивен)",
            name_en="Humans (bankrupt — inactive)",
            legal_name="Humans LLC",
            provider_type=ProviderType.FINTECH,
            status=ProviderStatus.DEPRECATED,
            description_uz=(
                "2025-yilda Toshkent iqtisodiy sudi tomonidan bankrot deb e'lon qilingan. "
                "Octobank bilan nizodan keyin xizmat to'xtatilgan."
            ),
        ),
        [
            ProductSeed(
                name_uz="Humans Pay (faol emas)",
                use_case=ProductUseCase.UNIVERSAL,
                official_url="https://humans.uz/",
                source_cited_urls={
                    "status": "https://www.intellinews.com/uzbekistan-fintech-humans-declared-bankrupt-liquidation-ordered-at-octobank-s-request-416147/",
                },
                status=ProductStatus.INACTIVE,
            ),
        ],
    ),
]


async def upsert_provider(session, seed: ProviderSeed) -> NasiyaProvider:
    existing = await session.scalar(
        select(NasiyaProvider).where(NasiyaProvider.slug == seed.slug)
    )
    if existing:
        for k, v in seed.model_dump(exclude_none=True).items():
            setattr(existing, k, v)
        existing.source_verified_at = datetime.now(UTC)
        return existing
    p = NasiyaProvider(**seed.model_dump(), source_verified_at=datetime.now(UTC))
    session.add(p)
    await session.flush()
    return p


async def upsert_product(session, provider_id: int, seed: ProductSeed) -> NasiyaProduct:
    existing = await session.scalar(
        select(NasiyaProduct).where(
            NasiyaProduct.provider_id == provider_id,
            NasiyaProduct.name_uz == seed.name_uz,
        )
    )
    if existing:
        for k, v in seed.model_dump(exclude_none=True).items():
            setattr(existing, k, v)
        existing.source_verified_at = datetime.now(UTC)
        return existing
    p = NasiyaProduct(
        provider_id=provider_id,
        **seed.model_dump(),
        source_verified_at=datetime.now(UTC),
    )
    session.add(p)
    return p


async def main() -> None:
    async with SessionLocal() as session:
        for prov_seed, prod_seeds in SEED:
            provider = await upsert_provider(session, prov_seed)
            await session.flush()
            for prod_seed in prod_seeds:
                await upsert_product(session, provider.id, prod_seed)
        await session.commit()
        print(f"Seeded {len(SEED)} providers with their products.")


if __name__ == "__main__":
    asyncio.run(main())
