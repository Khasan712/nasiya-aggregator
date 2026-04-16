"""Reusable FastAPI dependencies — DB session, current user, RBAC."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def is_service_request(
    x_service_token: Annotated[str | None, Header(alias="X-Service-Token")] = None,
) -> bool:
    """True if the caller presented the trusted internal service token."""
    return bool(
        settings.service_token
        and x_service_token
        and x_service_token == settings.service_token
    )


async def get_current_user(
    db: DbDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or blocked")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed: UserRole):
    async def _checker(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return _checker


require_editor = require_role(UserRole.EDITOR, UserRole.ADMIN)
require_admin = require_role(UserRole.ADMIN)


async def require_editor_or_service(
    db: DbDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    is_service: Annotated[bool, Depends(is_service_request)],
) -> User | None:
    """Allow either a logged-in editor/admin OR the trusted dashboard service.

    Returns the User if a real one authenticated, else None for service calls.
    """
    if is_service:
        return None
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user = await get_current_user(db, token)
    if user.role not in (UserRole.EDITOR, UserRole.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    return user


async def require_admin_or_service(
    db: DbDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    is_service: Annotated[bool, Depends(is_service_request)],
) -> User | None:
    if is_service:
        return None
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user = await get_current_user(db, token)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user
