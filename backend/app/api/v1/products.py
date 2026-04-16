"""CRUD endpoints for nasiya products."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DbDep, require_admin_or_service, require_editor_or_service
from app.models.product import NasiyaProduct, ProductStatus
from app.models.provider import NasiyaProvider
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
async def list_products(
    db: DbDep,
    provider_id: int | None = None,
    amount_uzs: int | None = Query(None, ge=0, description="Show products that cover this amount"),
    status_filter: Annotated[ProductStatus | None, Query(alias="status")] = None,
    include_inactive: bool = Query(False, description="Include status=inactive rows"),
    limit: int = Query(100, le=500),
    offset: int = 0,
) -> list[NasiyaProduct]:
    stmt = (
        select(NasiyaProduct)
        .options(selectinload(NasiyaProduct.provider))
        .order_by(NasiyaProduct.id)
        .limit(limit)
        .offset(offset)
    )
    if provider_id:
        stmt = stmt.where(NasiyaProduct.provider_id == provider_id)
    if status_filter:
        # Explicit filter wins.
        stmt = stmt.where(NasiyaProduct.status == status_filter)
    elif not include_inactive:
        # Default: show active + needs_verification, hide inactive so deprecated
        # or retired products don't leak into the bot/public views.
        stmt = stmt.where(NasiyaProduct.status != ProductStatus.INACTIVE)
    if amount_uzs is not None:
        stmt = stmt.where(
            NasiyaProduct.max_limit_uzs.is_(None) | (NasiyaProduct.max_limit_uzs >= amount_uzs)
        )
    return list((await db.scalars(stmt)).all())


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: DbDep) -> NasiyaProduct:
    p = await db.get(NasiyaProduct, product_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return p


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_editor_or_service)],
)
async def create_product(payload: ProductCreate, db: DbDep) -> NasiyaProduct:
    if not await db.get(NasiyaProvider, payload.provider_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    p = NasiyaProduct(**payload.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_editor_or_service)],
)
async def update_product(
    product_id: int, payload: ProductUpdate, db: DbDep
) -> NasiyaProduct:
    p = await db.get(NasiyaProduct, product_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    await db.commit()
    await db.refresh(p)
    return p


@router.post(
    "/{product_id}/verify",
    response_model=ProductRead,
    dependencies=[Depends(require_editor_or_service)],
)
async def mark_verified(product_id: int, db: DbDep) -> NasiyaProduct:
    p = await db.get(NasiyaProduct, product_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    p.source_verified_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_or_service)],
)
async def delete_product(product_id: int, db: DbDep) -> None:
    p = await db.get(NasiyaProduct, product_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    await db.delete(p)
    await db.commit()
