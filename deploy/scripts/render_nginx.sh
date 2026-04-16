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

# Load only the vars we care about, with defaults that match compose files.
# shellcheck source=/dev/null
set -a; . ./.env; set +a
export BACKEND_HOST_PORT="${BACKEND_HOST_PORT:-8000}"
export DASHBOARD_HOST_PORT="${DASHBOARD_HOST_PORT:-3000}"
# server_name — IP yoki domain. Default: catch-all `_` (lekin mavjud nginx
# config'da `_` allaqachon bo'lsa, .env'da real IP/domain yozish tavsiya etiladi).
export NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-_}"
# `NGINX_DEFAULT_SERVER=default_server` bo'lsa — nasiya host-header mos kelmagan
# so'rovlar uchun ham javob beradi (IP bilan kirish uchun kerak). Bo'sh bo'lsa
# faqat server_name matchga javob beradi.
# Server'da boshqa default_server (masalan sites-enabled/default) yo'qligiga
# ishonch hosil qilib qo'ying: `grep -r "default_server" /etc/nginx/`
export NGINX_DEFAULT_SERVER="${NGINX_DEFAULT_SERVER:-}"

# Render to a temp file first so we can compare and avoid an unnecessary reload.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

# Substitute exactly the variables we care about. Prefer envsubst (gettext) on
# Linux servers; fall back to plain sed when it's missing (macOS dev boxes).
if command -v envsubst >/dev/null 2>&1; then
  envsubst '${BACKEND_HOST_PORT} ${DASHBOARD_HOST_PORT} ${NGINX_SERVER_NAME} ${NGINX_DEFAULT_SERVER}' < "$TEMPLATE" > "$TMP"
else
  /usr/bin/sed \
    -e "s|\${BACKEND_HOST_PORT}|$BACKEND_HOST_PORT|g" \
    -e "s|\${DASHBOARD_HOST_PORT}|$DASHBOARD_HOST_PORT|g" \
    -e "s|\${NGINX_SERVER_NAME}|$NGINX_SERVER_NAME|g" \
    -e "s|\${NGINX_DEFAULT_SERVER}|$NGINX_DEFAULT_SERVER|g" \
    "$TEMPLATE" > "$TMP"
fi

# Tidy up: if NGINX_DEFAULT_SERVER is empty, remove the trailing space before ;
/usr/bin/sed -i.bak -E 's/(listen [^;]*[^ ;]) +;/\1;/g; s/(listen [^;]*) +;/\1;/g' "$TMP"
/bin/rm -f "${TMP}.bak"

echo "→ Rendered template:"
echo "    BACKEND_HOST_PORT    = $BACKEND_HOST_PORT"
echo "    DASHBOARD_HOST_PORT  = $DASHBOARD_HOST_PORT"
echo "    NGINX_SERVER_NAME    = $NGINX_SERVER_NAME"
echo "    NGINX_DEFAULT_SERVER = ${NGINX_DEFAULT_SERVER:-(not default)}"
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
