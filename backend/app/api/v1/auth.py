"""Auth endpoints — email/password login + Telegram Login Widget."""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import (
    LoginRequest,
    TelegramLoginPayload,
    TokenPair,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DbDep) -> User:
    """Register a dashboard user. In production this should be admin-gated; for MVP open."""
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: DbDep) -> TokenPair:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is blocked")
    user.last_seen_at = datetime.now(UTC)
    await db.commit()
    return TokenPair(
        access_token=create_access_token(user.id, extra={"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/telegram", response_model=TokenPair)
async def telegram_login(payload: TelegramLoginPayload, db: DbDep) -> TokenPair:
    """Verify Telegram Login Widget signature, create/find user, issue tokens.

    See: https://core.telegram.org/widgets/login#checking-authorization
    """
    if not settings.bot_token:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Bot token not configured")

    data = payload.model_dump(exclude_none=True)
    received_hash = data.pop("hash")
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data))
    secret_key = hashlib.sha256(settings.bot_token.encode()).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Telegram signature invalid")

    user = await db.scalar(select(User).where(User.telegram_id == payload.id))
    is_admin_seed = payload.id in settings.bot_admin_ids
    if not user:
        user = User(
            telegram_id=payload.id,
            telegram_username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=UserRole.ADMIN if is_admin_seed else UserRole.USER,
        )
        db.add(user)
    else:
        user.telegram_username = payload.username or user.telegram_username
        user.first_name = payload.first_name or user.first_name
        user.last_name = payload.last_name or user.last_name
        if is_admin_seed and user.role == UserRole.USER:
            user.role = UserRole.ADMIN
    user.last_seen_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)

    return TokenPair(
        access_token=create_access_token(user.id, extra={"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> User:
    return user
