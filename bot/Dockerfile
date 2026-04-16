# syntax=docker/dockerfile:1.7
# ─── Stage 1: build the venv with uv ──────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY app ./app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ─── Stage 2: runtime ─────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    TZ=Asia/Tashkent

RUN apt-get update \
 && apt-get install -y --no-install-recommends procps tzdata \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r app && useradd -r -g app -d /app -s /bin/bash app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app

# Long-polling has no port — health is "process is alive AND aiogram dispatcher running".
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD pgrep -f "python -m app.main" > /dev/null || exit 1

CMD ["python", "-m", "app.main"]
