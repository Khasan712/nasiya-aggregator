"""Audit log for the daily official-URL re-verification job."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class UrlCheckLog(Base, TimestampMixin):
    __tablename__ = "url_check_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), index=True)  # 'provider' | 'product'
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    field_name: Mapped[str] = mapped_column(String(64))  # e.g. 'official_url'
    url: Mapped[str] = mapped_column(String(500))
    status_code: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    is_ok: Mapped[bool] = mapped_column(Boolean, index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
