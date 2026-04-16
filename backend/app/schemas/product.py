"""Pydantic schemas for NasiyaProduct."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import ProductStatus, ProductUseCase


class ProductBase(BaseModel):
    provider_id: int
    name_uz: str = Field(min_length=1, max_length=255)
    name_ru: str | None = None
    name_en: str | None = None

    min_limit_uzs: int | None = Field(default=None, ge=0)
    max_limit_uzs: int | None = Field(default=None, ge=0)

    min_term_months: int | None = Field(default=None, ge=0)
    max_term_months: int | None = Field(default=None, ge=0)
    allowed_terms: list[int] | None = None

    is_interest_free: bool = False
    markup_rate: Decimal | None = Field(default=None, ge=0)
    markup_note_uz: str | None = None

    min_age: int | None = Field(default=None, ge=0, le=120)
    max_age: int | None = Field(default=None, ge=0, le=120)
    citizenship_required: str | None = None
    min_income_uzs: int | None = Field(default=None, ge=0)
    eligibility_note_uz: str | None = None

    use_case: ProductUseCase | None = None

    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None

    official_url: str | None = None
    ios_app_url: str | None = None
    android_app_url: str | None = None
    telegram_bot: str | None = None
    telegram_channel: str | None = None
    support_phone: str | None = None
    support_email: str | None = None
    partners_count: int | None = Field(default=None, ge=0)
    partners_list_url: str | None = None

    source_cited_urls: dict[str, Any] | None = None
    status: ProductStatus = ProductStatus.ACTIVE


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name_uz: str | None = None
    name_ru: str | None = None
    name_en: str | None = None
    min_limit_uzs: int | None = None
    max_limit_uzs: int | None = None
    min_term_months: int | None = None
    max_term_months: int | None = None
    allowed_terms: list[int] | None = None
    is_interest_free: bool | None = None
    markup_rate: Decimal | None = None
    markup_note_uz: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    citizenship_required: str | None = None
    min_income_uzs: int | None = None
    eligibility_note_uz: str | None = None
    use_case: ProductUseCase | None = None
    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None
    official_url: str | None = None
    ios_app_url: str | None = None
    android_app_url: str | None = None
    telegram_bot: str | None = None
    telegram_channel: str | None = None
    support_phone: str | None = None
    support_email: str | None = None
    partners_count: int | None = None
    partners_list_url: str | None = None
    source_cited_urls: dict[str, Any] | None = None
    status: ProductStatus | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
