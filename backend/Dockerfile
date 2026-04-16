# syntax=docker/dockerfile:1.7
# ─── Stage 1: build the venv with uv ──────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install only the runtime deps first (cache-friendly).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Now copy the source and finalize the install.
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ─── Stage 2: runtime ─────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    TZ=Asia/Tashkent

# Minimal runtime tools: curl for healthchecks, tzdata for Asia/Tashkent.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl tzdata \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r app && useradd -r -g app -d /app -s /bin/bash app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

# 2 workers — fits a small VPS. Increase via compose `command:` override on bigger boxes.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
