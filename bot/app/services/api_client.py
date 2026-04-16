"""Thin HTTP client around the FastAPI backend."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel

from app.config import settings


class Provider(BaseModel):
    id: int
    slug: str
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    provider_type: str
    status: str
    description_uz: str | None = None


class Product(BaseModel):
    id: int
    provider_id: int
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
    official_url: str | None = None
    ios_app_url: str | None = None
    android_app_url: str | None = None
    telegram_bot: str | None = None
    support_phone: str | None = None
    support_email: str | None = None
    status: str = "active"  # "active" | "needs_verification" | "inactive"


class BackendClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url or settings.backend_url,
            timeout=10.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def list_providers(self) -> list[Provider]:
        # Backend default: show active + needs_verification, hide inactive.
        r = await self._client.get("/api/v1/providers")
        r.raise_for_status()
        return [Provider.model_validate(p) for p in r.json()]

    async def list_products(self, *, amount_uzs: int | None = None) -> list[Product]:
        # Backend default: show active + needs_verification, hide inactive.
        params: dict[str, Any] = {}
        if amount_uzs is not None:
            params["amount_uzs"] = amount_uzs
        r = await self._client.get("/api/v1/products", params=params)
        r.raise_for_status()
        return [Product.model_validate(p) for p in r.json()]

    async def get_product(self, product_id: int) -> Product:
        r = await self._client.get(f"/api/v1/products/{product_id}")
        r.raise_for_status()
        return Product.model_validate(r.json())


backend = BackendClient()
