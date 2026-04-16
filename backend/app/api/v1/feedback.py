"""Feedback list + resolve endpoints (dashboard side)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select

from app.api.deps import DbDep, is_service_request, oauth2_scheme
from app.core.security import decode_token
from app.models.feedback import Feedback
from app.models.user import User, UserRole
from app.schemas.feedback import FeedbackList, FeedbackRow

router = APIRouter(prefix="/feedback", tags=["feedback"])


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


@router.get("", response_model=FeedbackList, dependencies=[Depends(_require_viewer_or_service)])
async def list_feedback(
    db: DbDep,
    only_open: bool = Query(False),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> FeedbackList:
    base = select(Feedback)
    count_q = select(func.count(Feedback.id))
    if only_open:
        base = base.where(Feedback.is_resolved.is_(False))
        count_q = count_q.where(Feedback.is_resolved.is_(False))

    total = int(await db.scalar(count_q) or 0)

    stmt = (
        base.order_by(desc(Feedback.created_at))
        .limit(limit)
        .offset(offset)
    )
    rows = list((await db.scalars(stmt)).all())

    # Fetch users in one query
    user_ids = {r.user_id for r in rows if r.user_id}
    users: dict[int, User] = {}
    if user_ids:
        users_rows = (await db.scalars(select(User).where(User.id.in_(user_ids)))).all()
        users = {u.id: u for u in users_rows}

    items: list[FeedbackRow] = []
    for r in rows:
        u = users.get(r.user_id) if r.user_id else None
        items.append(
            FeedbackRow(
                id=r.id,
                user_id=r.user_id,
                text=r.text,
                language=r.language,
                is_resolved=r.is_resolved,
                created_at=r.created_at,
                user_first_name=u.first_name if u else None,
                user_telegram_username=u.telegram_username if u else None,
                user_telegram_id=u.telegram_id if u else None,
            )
        )
    return FeedbackList(total=total, items=items)


@router.post(
    "/{feedback_id}/resolve",
    response_model=FeedbackRow,
    dependencies=[Depends(_require_viewer_or_service)],
)
async def mark_resolved(feedback_id: int, db: DbDep) -> FeedbackRow:
    fb = await db.get(Feedback, feedback_id)
    if not fb:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Feedback not found")
    fb.is_resolved = not fb.is_resolved  # toggle
    await db.commit()
    await db.refresh(fb)
    user = await db.get(User, fb.user_id) if fb.user_id else None
    return FeedbackRow(
        id=fb.id,
        user_id=fb.user_id,
        text=fb.text,
        language=fb.language,
        is_resolved=fb.is_resolved,
        created_at=fb.created_at,
        user_first_name=user.first_name if user else None,
        user_telegram_username=user.telegram_username if user else None,
        user_telegram_id=user.telegram_id if user else None,
    )
