"""Endpoints called by the Telegram bot (service-token authenticated)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import DbDep, is_service_request
from app.models.event import BotEvent
from app.models.feedback import Feedback
from app.models.user import User, UserLanguage, UserRole
from app.schemas.event import BotEventCreate, BotEventRead
from app.schemas.feedback import FeedbackCreate, FeedbackRow

router = APIRouter(prefix="/bot", tags=["bot"])


async def _require_service(is_service: Annotated[bool, Depends(is_service_request)]) -> None:
    if not is_service:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Service token required")


@router.post(
    "/events",
    response_model=BotEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_require_service)],
)
async def post_event(payload: BotEventCreate, db: DbDep) -> BotEvent:
    """Upsert the bot user, then record the event. Idempotent for the user upsert."""
    user = await db.scalar(select(User).where(User.telegram_id == payload.telegram_id))
    if user is None:
        user = User(
            telegram_id=payload.telegram_id,
            telegram_username=payload.telegram_username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            language=payload.language or UserLanguage.UZ,
            role=UserRole.USER,
        )
        db.add(user)
        await db.flush()
    else:
        if payload.telegram_username:
            user.telegram_username = payload.telegram_username
        if payload.first_name:
            user.first_name = payload.first_name
        if payload.last_name:
            user.last_name = payload.last_name
        if payload.language:
            user.language = payload.language
        user.last_seen_at = datetime.now(UTC)

    event = BotEvent(
        user_id=user.id,
        event_type=payload.event_type,
        product_id=payload.product_id,
        payload=payload.payload,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def _upsert_user(db, payload: FeedbackCreate) -> User:
    user = await db.scalar(select(User).where(User.telegram_id == payload.telegram_id))
    if user is None:
        user = User(
            telegram_id=payload.telegram_id,
            telegram_username=payload.telegram_username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            language=payload.language or UserLanguage.UZ,
            role=UserRole.USER,
        )
        db.add(user)
        await db.flush()
    else:
        if payload.telegram_username:
            user.telegram_username = payload.telegram_username
        if payload.first_name:
            user.first_name = payload.first_name
        if payload.last_name:
            user.last_name = payload.last_name
        if payload.language:
            user.language = payload.language
        user.last_seen_at = datetime.now(UTC)
    return user


@router.post(
    "/feedback",
    response_model=FeedbackRow,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_require_service)],
)
async def post_feedback(payload: FeedbackCreate, db: DbDep) -> FeedbackRow:
    user = await _upsert_user(db, payload)
    fb = Feedback(user_id=user.id, text=payload.text, language=payload.language)
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return FeedbackRow(
        id=fb.id,
        user_id=fb.user_id,
        text=fb.text,
        language=fb.language,
        is_resolved=fb.is_resolved,
        created_at=fb.created_at,
        user_first_name=user.first_name,
        user_telegram_username=user.telegram_username,
        user_telegram_id=user.telegram_id,
    )
