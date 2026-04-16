"""Admin audit log — who changed what."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AdminAuditLog(Base, TimestampMixin):
    __tablename__ = "admin_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    action: Mapped[str] = mapped_column(String(64))           # e.g. "create", "update", "delete"
    entity_type: Mapped[str] = mapped_column(String(64))      # "provider", "product", "user"
    entity_id: Mapped[int | None]
    before: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSON)
