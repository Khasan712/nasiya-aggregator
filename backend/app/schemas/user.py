"""Pydantic schemas for User and auth flows."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserLanguage, UserRole


class UserBase(BaseModel):
    email: EmailStr | None = None
    telegram_id: int | None = None
    telegram_username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    language: UserLanguage = UserLanguage.UZ
    role: UserRole = UserRole.USER


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TelegramLoginPayload(BaseModel):
    """Payload from Telegram Login Widget — see https://core.telegram.org/widgets/login"""

    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str
