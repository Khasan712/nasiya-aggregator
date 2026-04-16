"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.scheduler import scheduler, setup_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("nasiya")


def _validate_production_safety() -> None:
    """Fail fast at boot if a prod-only requirement is missing."""
    if not settings.is_production:
        return
    problems: list[str] = []
    if settings.secret_key in ("", "change-me-32-bytes-hex") or len(settings.secret_key) < 32:
        problems.append("SECRET_KEY missing or too short (need >= 32 chars, generate with `openssl rand -hex 32`)")
    if not settings.service_token or len(settings.service_token) < 24:
        problems.append("SERVICE_TOKEN missing (generate with `openssl rand -hex 24`)")
    if not settings.cors_origins:
        log.warning("CORS_ORIGINS is empty in production — dashboard cookie auth will not work")
    if problems:
        raise RuntimeError("Production safety check failed:\n  - " + "\n  - ".join(problems))


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_production_safety()
    setup_jobs()
    scheduler.start()
    log.info(
        "nasiya backend started (env=%s) — scheduled jobs: %s",
        settings.app_env,
        [(j.id, str(j.next_run_time)) for j in scheduler.get_jobs()],
    )
    yield
    scheduler.shutdown(wait=False)
    log.info("scheduler stopped")


def create_app() -> FastAPI:
    # In production, hide auto-generated docs (no Swagger / ReDoc / OpenAPI schema)
    # to reduce surface area. Dev keeps them for convenience.
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"
    openapi_url = None if settings.is_production else "/openapi.json"

    app = FastAPI(
        title="Nasiya Aggregator API",
        version="0.1.0",
        description="O'zbekistondagi nasiya xizmatlari uchun rasmiy ma'lumot agregatori.",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        info: dict[str, str] = {"app": settings.app_name, "env": settings.app_env}
        if not settings.is_production:
            info["docs"] = "/docs"
        return info

    return app


app = create_app()
