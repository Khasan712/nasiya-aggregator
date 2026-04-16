"""Concrete nasiya product offered by a provider."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.provider import NasiyaProvider


class ProductUseCase(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNIVERSAL = "universal"
    CASH = "cash"
    AUTO = "auto"


class ProductStatus(StrEnum):
    ACTIVE = "active"
    NEEDS_VERIFICATION = "needs_verification"
    INACTIVE = "inactive"


class NasiyaProduct(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        index=True,
    )

    name_uz: Mapped[str] = mapped_column(String(255))
    name_ru: Mapped[str | None] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255))

    # Limits in UZS (integer som — stored as BigInteger because UZS values are large)
    min_limit_uzs: Mapped[int | None] = mapped_column(BigInteger)
    max_limit_uzs: Mapped[int | None] = mapped_column(BigInteger)

    # Term in months
    min_term_months: Mapped[int | None] = mapped_column(Integer)
    max_term_months: Mapped[int | None] = mapped_column(Integer)
    allowed_terms: Mapped[list[int] | None] = mapped_column(JSON)  # e.g. [3, 6, 12]

    # Cost
    is_interest_free: Mapped[bool] = mapped_column(Boolean, default=False)
    markup_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))  # percent, e.g. 15.000
    markup_note_uz: Mapped[str | None] = mapped_column(Text)

    # Eligibility
    min_age: Mapped[int | None] = mapped_column(Integer)
    max_age: Mapped[int | None] = mapped_column(Integer)
    citizenship_required: Mapped[str | None] = mapped_column(String(64))  # "UZ"
    min_income_uzs: Mapped[int | None] = mapped_column(BigInteger)
    eligibility_note_uz: Mapped[str | None] = mapped_column(Text)

    use_case: Mapped[ProductUseCase | None] = mapped_column(
        SAEnum(ProductUseCase, name="product_use_case")
    )

    description_uz: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)

    # Official channels
    official_url: Mapped[str | None] = mapped_column(String(500))
    ios_app_url: Mapped[str | None] = mapped_column(String(500))
    android_app_url: Mapped[str | None] = mapped_column(String(500))
    telegram_bot: Mapped[str | None] = mapped_column(String(128))
    telegram_channel: Mapped[str | None] = mapped_column(String(128))
    support_phone: Mapped[str | None] = mapped_column(String(64))
    support_email: Mapped[str | None] = mapped_column(String(128))
    partners_count: Mapped[int | None] = mapped_column(Integer)
    partners_list_url: Mapped[str | None] = mapped_column(String(500))

    # Per-field source URL audit trail. Schema:
    #   { "max_limit_uzs": "https://...", "allowed_terms": "https://...", ... }
    source_cited_urls: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    status: Mapped[ProductStatus] = mapped_column(
        SAEnum(ProductStatus, name="product_status"),
        default=ProductStatus.ACTIVE,
    )
    source_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    provider: Mapped[NasiyaProvider] = relationship(back_populates="products")
