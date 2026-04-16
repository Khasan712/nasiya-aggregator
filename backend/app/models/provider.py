"""Nasiya provider — the legal entity (bank / MFO / fintech)."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import NasiyaProduct


class ProviderType(StrEnum):
    BANK = "bank"
    MFO = "mfo"
    FINTECH = "fintech"
    ISLAMIC = "islamic"


class ProviderStatus(StrEnum):
    ACTIVE = "active"
    NEEDS_VERIFICATION = "needs_verification"
    DEPRECATED = "deprecated"
    COMING_SOON = "coming_soon"


class NasiyaProvider(Base, TimestampMixin):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_uz: Mapped[str] = mapped_column(String(255))
    name_ru: Mapped[str | None] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255))
    legal_name: Mapped[str | None] = mapped_column(String(255))

    logo_url: Mapped[str | None] = mapped_column(String(500))
    brand_color: Mapped[str | None] = mapped_column(String(16))

    provider_type: Mapped[ProviderType] = mapped_column(SAEnum(ProviderType, name="provider_type"))
    status: Mapped[ProviderStatus] = mapped_column(
        SAEnum(ProviderStatus, name="provider_status"),
        default=ProviderStatus.ACTIVE,
    )

    license_body: Mapped[str | None] = mapped_column(String(64))  # e.g. "CBU", "MRTKR"
    license_number: Mapped[str | None] = mapped_column(String(64))
    license_date: Mapped[date | None] = mapped_column(Date)
    license_url: Mapped[str | None] = mapped_column(String(500))  # CBU registry URL

    description_uz: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)

    source_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    products: Mapped[list[NasiyaProduct]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )
