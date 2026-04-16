#!/usr/bin/env bash
# Postgres backup — pg_dump from the running container.
#
# Cron'ga ulash (server'da deployer foydalanuvchisi sifatida):
#   crontab -e
#   0 3 * * *  /opt/nasiya/deploy/scripts/backup.sh >> /opt/nasiya/backups/backup.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

BACKUP_DIR="$REPO_ROOT/backups"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP="$(date -u +'%Y%m%d_%H%M%S')"
DUMP_FILE="$BACKUP_DIR/nasiya_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

# .env'dan POSTGRES_USER/DB ni olamiz
# shellcheck source=/dev/null
set -a; . ./.env; set +a

echo "▶ pg_dump → $DUMP_FILE"
docker exec nasiya-postgres \
  pg_dump -U "${POSTGRES_USER:-nasiya}" -d "${POSTGRES_DB:-nasiya}" --no-owner --clean --if-exists \
  | gzip -9 > "$DUMP_FILE"

SIZE="$(du -h "$DUMP_FILE" | cut -f1)"
echo "✓ Backup OK ($SIZE)"

echo "▶ Eskirganlarni tozalash (> ${RETENTION_DAYS} kun)"
find "$BACKUP_DIR" -name 'nasiya_*.sql.gz' -mtime +"$RETENTION_DAYS" -print -delete

echo "✓ Done"
