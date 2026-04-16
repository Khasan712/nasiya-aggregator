"""Seed (or rotate) the default dashboard admin.

Defaults: admin@nasiya.uz / admin12345
Override via env: ADMIN_EMAIL, ADMIN_PASSWORD.

Run:
    uv run python -m app.scripts.seed_admin
"""

from __future__ import annotations

import asyncio
import os

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole


async def main() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@nasiya.uz")
    password = os.environ.get("ADMIN_PASSWORD", "admin12345")

    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing:
            existing.password_hash = hash_password(password)
            existing.role = UserRole.ADMIN
            existing.is_active = True
            print(f"Updated admin {email} (id={existing.id})")
        else:
            user = User(
                email=email,
                password_hash=hash_password(password),
                role=UserRole.ADMIN,
                first_name="Admin",
            )
            session.add(user)
            print(f"Created admin {email}")
        await session.commit()
    print(f"  password: {password}")


if __name__ == "__main__":
    asyncio.run(main())
