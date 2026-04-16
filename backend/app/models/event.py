"""Bot interaction events for analytics."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BotEventType(StrEnum):
    START = "start"
    VIEW_LIST = "view_list"
    VIEW_PROVIDER = "view_provider"
    VIEW_PRODUCT = "view_product"
    CLICK_OFFICIAL_LINK = "click_official_link"
    SEARCH_BY_AMOUNT = "search_by_amount"
    COMPARE = "compare"
    LANGUAGE_CHANGE = "language_change"
    FEEDBACK = "feedback"


class BotEvent(Base, TimestampMixin):
    __tablename__ = "bot_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    event_type: Mapped[BotEventType] = mapped_column(
        SAEnum(BotEventType, name="bot_event_type"),
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        index=True,
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
