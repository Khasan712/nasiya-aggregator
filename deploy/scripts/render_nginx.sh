#!/usr/bin/env bash
# Render the nginx config from the template, substituting host port values
# from .env. Writes the result to a destination path (default:
# /etc/nginx/conf.d/nasiya.conf), then runs `nginx -t` and reloads if the
# result actually changed.
#
# Usage:  ./deploy/scripts/render_nginx.sh [destination-path]
# Default destination: /etc/nginx/conf.d/nasiya.conf

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

TEMPLATE="deploy/nginx/nasiya.conf.template"
DEST="${1:-/etc/nginx/conf.d/nasiya.conf}"

if [[ ! -f .env ]]; then
  echo "✗ .env not found in $REPO_ROOT" >&2
  exit 1
fi

# Load only the port vars we care about, with defaults that match compose files.
# shellcheck source=/dev/null
set -a; . ./.env; set +a
export BACKEND_HOST_PORT="${BACKEND_HOST_PORT:-8000}"
export DASHBOARD_HOST_PORT="${DASHBOARD_HOST_PORT:-3000}"

# Render to a temp file first so we can compare and avoid an unnecessary reload.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

# Substitute exactly the variables we care about. Prefer envsubst (gettext) on
# Linux servers; fall back to plain sed when it's missing (macOS dev boxes).
if command -v envsubst >/dev/null 2>&1; then
  envsubst '${BACKEND_HOST_PORT} ${DASHBOARD_HOST_PORT}' < "$TEMPLATE" > "$TMP"
else
  /usr/bin/sed \
    -e "s/\${BACKEND_HOST_PORT}/$BACKEND_HOST_PORT/g" \
    -e "s/\${DASHBOARD_HOST_PORT}/$DASHBOARD_HOST_PORT/g" \
    "$TEMPLATE" > "$TMP"
fi

echo "→ Rendered template:"
echo "    BACKEND_HOST_PORT  = $BACKEND_HOST_PORT"
echo "    DASHBOARD_HOST_PORT = $DASHBOARD_HOST_PORT"
echo "    destination = $DEST"

# Detect if the destination needs writing (idempotent).
if [[ -f "$DEST" ]] && /usr/bin/cmp -s "$TMP" "$DEST"; then
  echo "✓ $DEST already up to date — nothing to do"
  exit 0
fi

# Write & reload (sudo if not root).
if [[ "$(id -u)" -ne 0 ]] && [[ "$DEST" == /etc/* ]]; then
  echo "→ /etc/* writes need sudo"
  sudo cp "$TMP" "$DEST"
  sudo nginx -t
  sudo systemctl reload nginx
else
  cp "$TMP" "$DEST"
  if command -v nginx >/dev/null 2>&1; then
    nginx -t
    if command -v systemctl >/dev/null 2>&1; then
      systemctl reload nginx
    fi
  fi
fi

echo "✓ nginx config updated and reloaded"
