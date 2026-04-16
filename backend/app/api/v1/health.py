"""Health & readiness checks."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.api.deps import DbDep

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    db: str


@router.get("/health", response_model=HealthResponse)
async def health(db: DbDep) -> HealthResponse:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:  # noqa: BLE001
        db_status = "down"
    return HealthResponse(status="ok", db=db_status)
