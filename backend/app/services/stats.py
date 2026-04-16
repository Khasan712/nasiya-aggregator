"""Aggregation queries for the admin dashboard's Statistics page."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import cast as sa_cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Date

from app.models.event import BotEvent, BotEventType
from app.models.product import NasiyaProduct
from app.models.provider import NasiyaProvider
from app.models.user import User
from app.schemas.event import (
    StatsAmountBucket,
    StatsAmountSummary,
    StatsCounter,
    StatsDailyPoint,
    StatsEventTypeRow,
    StatsFunnelStep,
    StatsHourlyPoint,
    StatsOverview,
    StatsTopProduct,
    StatsTopProvider,
)


def _now() -> datetime:
    return datetime.now(UTC)


async def _counter(db: AsyncSession, model, base_where=None) -> StatsCounter:
    """Returns today / 7d / 30d / total counts for `model` rows."""
    now = _now()

    async def _count(since: datetime | None) -> int:
        stmt = select(func.count(model.id))
        if base_where is not None:
            stmt = stmt.where(base_where)
        if since is not None:
            stmt = stmt.where(model.created_at >= since)
        return int(await db.scalar(stmt) or 0)

    return StatsCounter(
        today=await _count(now - timedelta(days=1)),
        last_7d=await _count(now - timedelta(days=7)),
        last_30d=await _count(now - timedelta(days=30)),
        total=await _count(None),
    )


# ─── Public API ────────────────────────────────────────────────────────────


async def overview(db: AsyncSession) -> StatsOverview:
    amounts = await _amount_values(db)
    return StatsOverview(
        users=await _counter(db, User),
        bot_users=await _counter(db, User, base_where=User.telegram_id.is_not(None)),
        events=await _counter(db, BotEvent),
        top_products=await _top_products(db),
        top_providers=await _top_providers(db),
        amount_buckets=_amount_buckets_from(amounts),
        amount_summary=_amount_summary_from(amounts),
        daily_activity=await _daily_activity(db),
        hourly_activity=await _hourly_activity(db),
        event_types=await _event_types(db),
        languages=await _languages(db),
        funnel=await _funnel(db),
    )


async def _top_products(db: AsyncSession, limit: int = 10) -> list[StatsTopProduct]:
    stmt = (
        select(
            NasiyaProduct.id,
            NasiyaProduct.name_uz,
            NasiyaProvider.name_uz.label("provider_name_uz"),
            func.count(BotEvent.id).label("views"),
        )
        .join(NasiyaProduct, NasiyaProduct.id == BotEvent.product_id)
        .join(NasiyaProvider, NasiyaProvider.id == NasiyaProduct.provider_id)
        .where(BotEvent.event_type == BotEventType.VIEW_PRODUCT)
        .group_by(NasiyaProduct.id, NasiyaProvider.name_uz)
        .order_by(func.count(BotEvent.id).desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [
        StatsTopProduct(
            product_id=r.id,
            name_uz=r.name_uz,
            provider_name_uz=r.provider_name_uz,
            views=r.views,
        )
        for r in rows
    ]


async def _amount_values(db: AsyncSession) -> list[int]:
    """All search_by_amount integer amounts from payload — used by buckets + summary."""
    stmt = select(BotEvent.payload).where(
        BotEvent.event_type == BotEventType.SEARCH_BY_AMOUNT
    )
    rows = (await db.execute(stmt)).all()
    out: list[int] = []
    for (payload,) in rows:
        if isinstance(payload, dict) and isinstance(payload.get("amount"), int):
            out.append(payload["amount"])
    return out


def _amount_buckets_from(amounts: list[int]) -> list[StatsAmountBucket]:
    BUCKETS: list[tuple[str, int, int]] = [
        ("< 1M", 0, 1_000_000),
        ("1–5M", 1_000_000, 5_000_000),
        ("5–10M", 5_000_000, 10_000_000),
        ("10–20M", 10_000_000, 20_000_000),
        ("20–50M", 20_000_000, 50_000_000),
        ("> 50M", 50_000_000, 10**18),
    ]
    out: list[StatsAmountBucket] = []
    for label, lo, hi in BUCKETS:
        n = sum(1 for v in amounts if lo <= v < hi)
        if n:
            out.append(StatsAmountBucket(bucket_label=label, count=n))
    return out


def _amount_summary_from(amounts: list[int]) -> StatsAmountSummary:
    if not amounts:
        return StatsAmountSummary(searches=0, avg_uzs=0, median_uzs=0, max_uzs=0)
    sorted_a = sorted(amounts)
    median = sorted_a[len(sorted_a) // 2]
    return StatsAmountSummary(
        searches=len(amounts),
        avg_uzs=sum(amounts) // len(amounts),
        median_uzs=median,
        max_uzs=max(amounts),
    )


async def _top_providers(db: AsyncSession, limit: int = 10) -> list[StatsTopProvider]:
    stmt = (
        select(
            NasiyaProvider.id,
            NasiyaProvider.name_uz,
            func.count(BotEvent.id).label("views"),
        )
        .join(NasiyaProduct, NasiyaProduct.provider_id == NasiyaProvider.id)
        .join(BotEvent, BotEvent.product_id == NasiyaProduct.id)
        .where(BotEvent.event_type == BotEventType.VIEW_PRODUCT)
        .group_by(NasiyaProvider.id)
        .order_by(func.count(BotEvent.id).desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [StatsTopProvider(provider_id=r.id, name_uz=r.name_uz, views=r.views) for r in rows]


async def _hourly_activity(db: AsyncSession) -> list[StatsHourlyPoint]:
    """Hourly histogram in Asia/Tashkent local time (UTC+5)."""
    # AT TIME ZONE shifts a `timestamptz` to wall-clock time in the named zone,
    # so a 03:00 UTC event correctly buckets into 08:00 Tashkent.
    local_ts = func.timezone("Asia/Tashkent", BotEvent.created_at)
    hour_col = func.extract("hour", local_ts)
    stmt = (
        select(hour_col.label("h"), func.count(BotEvent.id).label("n"))
        .group_by("h")
        .order_by("h")
    )
    rows = (await db.execute(stmt)).all()
    by_hour = {int(r.h): r.n for r in rows}
    return [StatsHourlyPoint(hour=h, events=by_hour.get(h, 0)) for h in range(24)]


async def _funnel(db: AsyncSession) -> list[StatsFunnelStep]:
    """A simple usage funnel (based on distinct users per step)."""
    async def _distinct_users(event_type: BotEventType) -> int:
        stmt = (
            select(func.count(func.distinct(BotEvent.user_id)))
            .where(BotEvent.event_type == event_type)
        )
        return int(await db.scalar(stmt) or 0)

    return [
        StatsFunnelStep(name="Bot start", count=await _distinct_users(BotEventType.START)),
        StatsFunnelStep(name="Ro'yxat / Qidiruv", count=await _distinct_users(BotEventType.VIEW_LIST) + await _distinct_users(BotEventType.SEARCH_BY_AMOUNT)),
        StatsFunnelStep(name="Mahsulot ochgan", count=await _distinct_users(BotEventType.VIEW_PRODUCT)),
        StatsFunnelStep(name="Solishtirgan", count=await _distinct_users(BotEventType.COMPARE)),
    ]


async def _daily_activity(db: AsyncSession, days: int = 30) -> list[StatsDailyPoint]:
    since = _now() - timedelta(days=days)
    day_col = sa_cast(BotEvent.created_at, Date)
    stmt = (
        select(
            day_col.label("day"),
            func.count(BotEvent.id).label("events"),
            func.count(func.distinct(BotEvent.user_id)).label("unique_users"),
        )
        .where(BotEvent.created_at >= since)
        .group_by(day_col)
        .order_by(day_col)
    )
    rows = (await db.execute(stmt)).all()
    return [
        StatsDailyPoint(day=r.day, events=r.events, unique_users=r.unique_users) for r in rows
    ]


async def _event_types(db: AsyncSession) -> list[StatsEventTypeRow]:
    stmt = (
        select(BotEvent.event_type, func.count(BotEvent.id))
        .group_by(BotEvent.event_type)
        .order_by(func.count(BotEvent.id).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [StatsEventTypeRow(event_type=str(r[0].value), count=r[1]) for r in rows]


async def _languages(db: AsyncSession) -> list[StatsEventTypeRow]:
    stmt = (
        select(User.language, func.count(User.id))
        .where(User.telegram_id.is_not(None))
        .group_by(User.language)
        .order_by(func.count(User.id).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [StatsEventTypeRow(event_type=str(r[0].value), count=r[1]) for r in rows]
