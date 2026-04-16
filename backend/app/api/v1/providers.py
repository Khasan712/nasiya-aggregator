"""CRUD endpoints for nasiya providers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DbDep, require_admin_or_service, require_editor_or_service
from app.models.provider import NasiyaProvider, ProviderStatus
from app.schemas.provider import ProviderCreate, ProviderRead, ProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderRead])
async def list_providers(
    db: DbDep,
    status_filter: Annotated[ProviderStatus | None, Query(alias="status")] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
) -> list[NasiyaProvider]:
    stmt = select(NasiyaProvider).order_by(NasiyaProvider.id).limit(limit).offset(offset)
    if status_filter:
        stmt = stmt.where(NasiyaProvider.status == status_filter)
    return list((await db.scalars(stmt)).all())


@router.get("/{provider_id}", response_model=ProviderRead)
async def get_provider(provider_id: int, db: DbDep) -> NasiyaProvider:
    p = await db.get(NasiyaProvider, provider_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    return p


@router.post(
    "",
    response_model=ProviderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_editor_or_service)],
)
async def create_provider(payload: ProviderCreate, db: DbDep) -> NasiyaProvider:
    if await db.scalar(select(NasiyaProvider).where(NasiyaProvider.slug == payload.slug)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Provider with this slug already exists")
    p = NasiyaProvider(**payload.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.patch(
    "/{provider_id}",
    response_model=ProviderRead,
    dependencies=[Depends(require_editor_or_service)],
)
async def update_provider(
    provider_id: int, payload: ProviderUpdate, db: DbDep
) -> NasiyaProvider:
    p = await db.get(NasiyaProvider, provider_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    await db.commit()
    await db.refresh(p)
    return p


@router.post(
    "/{provider_id}/verify",
    response_model=ProviderRead,
    dependencies=[Depends(require_editor_or_service)],
)
async def mark_verified(provider_id: int, db: DbDep) -> NasiyaProvider:
    """Mark provider info as freshly verified against official sources."""
    p = await db.get(NasiyaProvider, provider_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    p.source_verified_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_service)],
)
async def delete_provider(provider_id: int, db: DbDep) -> None:
    p = await db.get(NasiyaProvider, provider_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    await db.delete(p)
    await db.commit()
