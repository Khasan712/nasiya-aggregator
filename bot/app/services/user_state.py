"""Per-user state in Redis: language preference + compare list.

Keys:
    lang:{user_id}    str    user's language (uz/ru/en)
    cmp:{user_id}     list   product IDs added to compare (max 3)
"""

from __future__ import annotations

from app.i18n import DEFAULT_LANG, SUPPORTED, Lang, detect_lang
from app.services.redis_client import redis

COMPARE_TTL_SECONDS = 60 * 60  # 1h
COMPARE_MAX = 3


# ─── Language ───────────────────────────────────────────────────────────────


async def get_lang(user_id: int, fallback_tg_code: str | None = None) -> Lang:
    cached = await redis.get(f"lang:{user_id}")
    if cached and cached in SUPPORTED:
        return cached  # type: ignore[return-value]
    detected = detect_lang(fallback_tg_code)
    await set_lang(user_id, detected)
    return detected


async def set_lang(user_id: int, lang: Lang) -> None:
    if lang not in SUPPORTED:
        lang = DEFAULT_LANG
    await redis.set(f"lang:{user_id}", lang)


# ─── Compare list ──────────────────────────────────────────────────────────


async def compare_add(user_id: int, product_id: int) -> tuple[bool, str]:
    """Returns (success, status). status ∈ {"added", "already", "full"}."""
    key = f"cmp:{user_id}"
    existing = await redis.lrange(key, 0, -1)
    if str(product_id) in existing:
        return False, "already"
    if len(existing) >= COMPARE_MAX:
        return False, "full"
    await redis.rpush(key, product_id)
    await redis.expire(key, COMPARE_TTL_SECONDS)
    return True, "added"


async def compare_count(user_id: int) -> int:
    return await redis.llen(f"cmp:{user_id}")


async def compare_get(user_id: int) -> list[int]:
    items = await redis.lrange(f"cmp:{user_id}", 0, -1)
    return [int(x) for x in items]


async def compare_clear(user_id: int) -> None:
    await redis.delete(f"cmp:{user_id}")


# ─── Last list context (so "back" from product card returns to the same list) ─


async def remember_list(user_id: int, kind: str, amount: int | None = None) -> None:
    """kind is 'all' or 'search'. For 'search', amount is required."""
    value = f"search:{amount}" if kind == "search" and amount else "all"
    await redis.set(f"last_list:{user_id}", value, ex=60 * 60)


async def recall_list(user_id: int) -> tuple[str, int | None]:
    """Returns ('all', None) or ('search', amount). Defaults to 'all'."""
    raw = await redis.get(f"last_list:{user_id}")
    if raw and raw.startswith("search:"):
        try:
            return "search", int(raw.split(":", 1)[1])
        except ValueError:
            return "all", None
    return "all", None
