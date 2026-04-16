"""Pydantic schemas for NasiyaProvider."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.provider import ProviderStatus, ProviderType


class ProviderBase(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    name_uz: str = Field(min_length=1, max_length=255)
    name_ru: str | None = None
    name_en: str | None = None
    legal_name: str | None = None
    logo_url: str | None = None
    brand_color: str | None = None
    provider_type: ProviderType
    status: ProviderStatus = ProviderStatus.ACTIVE
    license_body: str | None = None
    license_number: str | None = None
    license_date: date | None = None
    license_url: str | None = None
    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name_uz: str | None = None
    name_ru: str | None = None
    name_en: str | None = None
    legal_name: str | None = None
    logo_url: str | None = None
    brand_color: str | None = None
    provider_type: ProviderType | None = None
    status: ProviderStatus | None = None
    license_body: str | None = None
    license_number: str | None = None
    license_date: date | None = None
    license_url: str | None = None
    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None


class ProviderRead(ProviderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
