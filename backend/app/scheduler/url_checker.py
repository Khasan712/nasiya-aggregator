"""Daily job: HEAD-check every official URL and notify admins of breakages."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Iterable

import httpx
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.product import NasiyaProduct
from app.models.provider import NasiyaProvider
from app.models.url_check import UrlCheckLog
from app.scheduler.notify import notify_admins

log = logging.getLogger(__name__)

# Fields on each model that should be reachable
PROVIDER_FIELDS: tuple[str, ...] = ("license_url",)
PRODUCT_FIELDS: tuple[str, ...] = (
    "official_url",
    "ios_app_url",
    "android_app_url",
    "partners_list_url",
)

USER_AGENT = (
    "Mozilla/5.0 (compatible; NasiyaAggregatorBot/0.1; +https://nasiya.local)"
)
TIMEOUT_SECONDS = 12.0
CONCURRENCY = 6


async def _check_one(
    client: httpx.AsyncClient,
    entity_type: str,
    entity_id: int,
    field_name: str,
    url: str,
) -> UrlCheckLog:
    start = time.time()
    status_code: int | None = None
    error: str | None = None
    try:
        r = await client.head(url, follow_redirects=True)
        # Many sites mishandle HEAD (return 404/405/501); fall back to GET to be sure.
        if r.status_code >= 400:
            r = await client.get(url, follow_redirects=True)
        status_code = r.status_code
    except Exception as exc:  # noqa: BLE001
        error = type(exc).__name__ + ": " + str(exc)[:300]
    elapsed_ms = int((time.time() - start) * 1000)
    return UrlCheckLog(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        url=url,
        status_code=status_code,
        response_time_ms=elapsed_ms,
        is_ok=status_code is not None and status_code < 400,
        error_message=error,
    )


def _gather_targets(providers, products) -> list[tuple[str, int, str, str]]:
    """Return [(entity_type, entity_id, field_name, url), …]"""
    out: list[tuple[str, int, str, str]] = []
    for p in providers:
        for f in PROVIDER_FIELDS:
            url = getattr(p, f, None)
            if url:
                out.append(("provider", p.id, f, url))
    for p in products:
        for f in PRODUCT_FIELDS:
            url = getattr(p, f, None)
            if url:
                out.append(("product", p.id, f, url))
    return out


async def run_url_checks() -> dict:
    """The scheduled job. Returns a small summary dict (also used by the manual trigger)."""
    log.info("url_check: starting")
    async with SessionLocal() as session:
        providers = list((await session.scalars(select(NasiyaProvider))).all())
        products = list((await session.scalars(select(NasiyaProduct))).all())
        targets = _gather_targets(providers, products)
        log.info("url_check: %d targets to check", len(targets))

        results: list[UrlCheckLog] = []
        sem = asyncio.Semaphore(CONCURRENCY)

        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        ) as client:
            async def _bounded(t):
                async with sem:
                    return await _check_one(client, *t)

            results = await asyncio.gather(*(_bounded(t) for t in targets))

        for r in results:
            session.add(r)
        await session.commit()

    broken = [r for r in results if not r.is_ok]
    summary = {"checked": len(results), "broken": len(broken)}
    log.info("url_check: done %s", summary)

    if broken:
        # Build admin notification
        lines = [f"🚨 <b>{len(broken)} ta rasmiy URL muammoli</b> ({len(results)} dan):", ""]
        for b in broken[:20]:
            status = b.status_code if b.status_code is not None else (b.error_message or "?")
            lines.append(
                f"• <b>{b.entity_type}#{b.entity_id}</b> [{b.field_name}]\n"
                f"  {b.url}\n"
                f"  → <code>{status}</code>"
            )
        if len(broken) > 20:
            lines.append(f"\n…va yana {len(broken) - 20} ta")
        await notify_admins("\n".join(lines))

    return summary
