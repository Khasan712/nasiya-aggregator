"""APScheduler — daily URL re-verification."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scheduler.url_checker import run_url_checks

log = logging.getLogger(__name__)

# Single shared scheduler instance — started/stopped via FastAPI lifespan.
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")


def setup_jobs() -> None:
    """Register cron jobs. Idempotent (safe to call again)."""
    scheduler.add_job(
        run_url_checks,
        trigger=CronTrigger(hour=3, minute=17),  # daily at 03:17 Tashkent local
        id="daily_url_check",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    log.info("scheduler: jobs registered (%s)", [j.id for j in scheduler.get_jobs()])
