#!/usr/bin/env bash
# Nasiya Aggregator — deploy a new version on the server.
#
# What it does:
#   1. git pull from the configured branch
#   2. Rebuild any docker images whose source changed
#   3. Apply pending Alembic migrations (one-shot container)
#   4. Restart backend / bot / dashboard with zero-downtime-ish rolling update
#   5. Show the resulting container status
#
# Usage:  ./deploy/scripts/deploy.sh [branch]
# Default branch: main

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

BRANCH="${1:-main}"
COMPOSE_FILE="docker-compose.prod.yml"

echo "━━━ Nasiya deploy ($(date -u +'%Y-%m-%d %H:%M:%S')Z) ━━━"
echo "→ Repo:   $REPO_ROOT"
echo "→ Branch: $BRANCH"
echo

if [[ ! -f .env ]]; then
  echo "✗ .env not found. cp .env.production.example .env and fill it in." >&2
  exit 1
fi

# ─── 1. Pull ─────────────────────────────────────────────────────────────
echo "▶ git pull origin $BRANCH"
git fetch --all --prune
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

# ─── 2. Build (cache-friendly) ───────────────────────────────────────────
echo
echo "▶ docker compose build"
docker compose -f "$COMPOSE_FILE" build

# ─── 3. Migrate ──────────────────────────────────────────────────────────
echo
echo "▶ alembic upgrade head"
docker compose -f "$COMPOSE_FILE" --profile migrate run --rm migrate

# ─── 4. Roll services ────────────────────────────────────────────────────
echo
echo "▶ docker compose up -d"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans postgres redis backend bot dashboard

# ─── 5. Health summary ───────────────────────────────────────────────────
echo
echo "▶ Status:"
sleep 4
docker compose -f "$COMPOSE_FILE" ps

echo
echo "▶ Recent logs (last 20 each):"
for svc in backend bot dashboard; do
  echo "  ── $svc ──"
  docker compose -f "$COMPOSE_FILE" logs --tail 20 "$svc" 2>&1 | sed 's/^/    /'
done

echo
echo "✓ Deploy finished."
