"""User feedback collected via the bot."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Feedback(Base, TimestampMixin):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(8))
    is_resolved: Mapped[bool] = mapped_column(default=False, index=True)
