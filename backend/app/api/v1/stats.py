"""Stats endpoint for the admin dashboard."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbDep, is_service_request, oauth2_scheme
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.schemas.event import StatsOverview
from app.services import stats as stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


async def _require_viewer_or_service(
    db: DbDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    is_service: Annotated[bool, Depends(is_service_request)],
) -> None:
    if is_service:
        return
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Auth required")
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    user = await db.get(User, int(payload["sub"]))
    if not user or user.role not in (UserRole.VIEWER, UserRole.EDITOR, UserRole.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")


@router.get("/overview", response_model=StatsOverview, dependencies=[Depends(_require_viewer_or_service)])
async def overview(db: DbDep) -> StatsOverview:
    return await stats_service.overview(db)
