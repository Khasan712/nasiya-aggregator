"""Application user — both bot users and dashboard admins."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class UserRole(StrEnum):
    USER = "user"      # bot user only
    VIEWER = "viewer"  # dashboard read-only
    EDITOR = "editor"  # dashboard CRUD
    ADMIN = "admin"    # full control


class UserLanguage(StrEnum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Telegram identity (nullable because email-only admins exist too)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(128))

    # Email identity (nullable for telegram-only bot users)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))

    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(32))

    language: Mapped[UserLanguage] = mapped_column(
        SAEnum(UserLanguage, name="user_language"),
        default=UserLanguage.UZ,
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.USER,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
