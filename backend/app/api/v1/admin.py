"""Admin-only operational endpoints (manual triggers, etc.)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.api.deps import DbDep, require_admin_or_service
from app.models.url_check import UrlCheckLog
from app.scheduler.url_checker import run_url_checks

router = APIRouter(prefix="/admin", tags=["admin"])


class RunSummary(BaseModel):
    checked: int
    broken: int


class UrlCheckRow(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    field_name: str
    url: str
    status_code: int | None
    response_time_ms: int | None
    is_ok: bool
    error_message: str | None
    created_at: datetime


@router.post(
    "/url-check/run",
    response_model=RunSummary,
    dependencies=[Depends(require_admin_or_service)],
)
async def trigger_url_check() -> RunSummary:
    """Manually run the daily URL check now (synchronously). Returns summary."""
    summary = await run_url_checks()
    return RunSummary(**summary)


@router.get(
    "/url-check/log",
    response_model=list[UrlCheckRow],
    dependencies=[Depends(require_admin_or_service)],
)
async def list_check_log(
    db: DbDep,
    only_broken: bool = Query(False),
    limit: int = Query(100, le=500),
) -> list[Any]:
    stmt = select(UrlCheckLog).order_by(desc(UrlCheckLog.created_at)).limit(limit)
    if only_broken:
        stmt = stmt.where(UrlCheckLog.is_ok.is_(False))
    return list((await db.scalars(stmt)).all())
