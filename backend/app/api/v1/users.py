"""Users listing for the dashboard (admin/editor/viewer allowed)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, desc, func, or_, select

from app.api.deps import DbDep, is_service_request, oauth2_scheme
from app.core.security import decode_token
from app.models.event import BotEvent
from app.models.user import User, UserLanguage, UserRole

router = APIRouter(prefix="/users", tags=["users"])


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


class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str | None
    telegram_id: int | None
    telegram_username: str | None
    first_name: str | None
    last_name: str | None
    language: UserLanguage
    role: UserRole
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime
    event_count: int = 0


class UsersResponse(BaseModel):
    total: int
    items: list[UserListItem]


@router.get("", response_model=UsersResponse, dependencies=[Depends(_require_viewer_or_service)])
async def list_users(
    db: DbDep,
    role: UserRole | None = Query(None),
    language: UserLanguage | None = Query(None),
    has_telegram: bool | None = Query(None),
    search: str | None = Query(None, description="Matches first_name, username, or email (ILIKE)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> UsersResponse:
    filters = []
    if role is not None:
        filters.append(User.role == role)
    if language is not None:
        filters.append(User.language == language)
    if has_telegram is not None:
        filters.append(User.telegram_id.is_not(None) if has_telegram else User.telegram_id.is_(None))
    if search:
        like = f"%{search}%"
        filters.append(
            or_(
                User.first_name.ilike(like),
                User.last_name.ilike(like),
                User.telegram_username.ilike(like),
                User.email.ilike(like),
            )
        )

    where_clause = and_(*filters) if filters else None

    total_stmt = select(func.count(User.id))
    if where_clause is not None:
        total_stmt = total_stmt.where(where_clause)
    total = int(await db.scalar(total_stmt) or 0)

    events_sq = (
        select(BotEvent.user_id, func.count(BotEvent.id).label("c"))
        .group_by(BotEvent.user_id)
        .subquery()
    )
    stmt = (
        select(User, func.coalesce(events_sq.c.c, 0).label("event_count"))
        .outerjoin(events_sq, events_sq.c.user_id == User.id)
        .order_by(desc(User.last_seen_at), desc(User.created_at))
        .limit(limit)
        .offset(offset)
    )
    if where_clause is not None:
        stmt = stmt.where(where_clause)

    rows = (await db.execute(stmt)).all()
    items: list[UserListItem] = []
    for user, event_count in rows:
        items.append(
            UserListItem(
                id=user.id,
                email=user.email,
                telegram_id=user.telegram_id,
                telegram_username=user.telegram_username,
                first_name=user.first_name,
                last_name=user.last_name,
                language=user.language,
                role=user.role,
                is_active=user.is_active,
                last_seen_at=user.last_seen_at,
                created_at=user.created_at,
                event_count=int(event_count),
            )
        )
    return UsersResponse(total=total, items=items)
