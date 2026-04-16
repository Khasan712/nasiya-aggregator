#!/usr/bin/env bash
# Nasiya Aggregator — first-time server bootstrap.
#
# Run ONCE on a fresh Ubuntu 22.04 / 24.04 server as root (or via sudo).
# After this, switch to the `deployer` user and run deploy/scripts/deploy.sh.

set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "✗ Bu skriptni root sifatida ishga tushiring (sudo)." >&2
  exit 1
fi

REPO_URL="https://github.com/Khasan712/nasiya-aggregator.git"
APP_DIR="/opt/nasiya"
DEPLOYER="deployer"

echo "━━━ Nasiya — server initial setup ━━━"

# ─── 1. Sistema yangilash ────────────────────────────────────────────────
echo "▶ apt update & install"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
    ca-certificates curl gnupg git nginx ufw \
    python3-certbot-nginx tzdata

# ─── 2. Docker Engine ────────────────────────────────────────────────────
if ! command -v docker >/dev/null 2>&1; then
  echo "▶ Docker o'rnatish (rasmiy script)"
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

# ─── 3. Deployer user ────────────────────────────────────────────────────
if ! id -u "$DEPLOYER" >/dev/null 2>&1; then
  echo "▶ Foydalanuvchi $DEPLOYER yaratilmoqda"
  useradd -m -s /bin/bash -G docker "$DEPLOYER"
fi
usermod -aG docker "$DEPLOYER"

# ─── 4. Repo klon ────────────────────────────────────────────────────────
mkdir -p "$APP_DIR"
chown -R "$DEPLOYER:$DEPLOYER" "$APP_DIR"
if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "▶ Repo klon: $REPO_URL → $APP_DIR"
  sudo -u "$DEPLOYER" git clone "$REPO_URL" "$APP_DIR"
else
  echo "▶ Repo allaqachon mavjud — o'tkazib yuborildi"
fi

# ─── 5. .env shabloni ────────────────────────────────────────────────────
if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "▶ .env shablon ko'chirildi"
  cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"
  chown "$DEPLOYER:$DEPLOYER" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo
  echo "  ⚠ MUHIM: $APP_DIR/.env ni tahrirlang va __CHANGE_ME__ qiymatlarini to'ldiring."
  echo "    nano $APP_DIR/.env"
fi

# ─── 6. Nginx config ─────────────────────────────────────────────────────
echo "▶ Nginx config /etc/nginx/conf.d/nasiya.conf ga ko'chirilmoqda"
cp "$APP_DIR/deploy/nginx/nasiya.conf" /etc/nginx/conf.d/nasiya.conf
# Default conf'ni o'chirish (default_server collision oldini olish uchun)
if [[ -f /etc/nginx/sites-enabled/default ]]; then
  rm /etc/nginx/sites-enabled/default
fi
nginx -t
systemctl reload nginx

# ─── 7. Firewall ─────────────────────────────────────────────────────────
echo "▶ UFW firewall sozlanmoqda (22, 80, 443)"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable

# ─── 8. Timezone ─────────────────────────────────────────────────────────
timedatectl set-timezone Asia/Tashkent || true

# ─── 9. Yakuniy ko'rsatma ────────────────────────────────────────────────
cat <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Server tayyor!

Keyingi qadamlar:
  1) cd $APP_DIR && nano .env             # __CHANGE_ME__ qiymatlarni to'ldiring
  2) sudo -u $DEPLOYER bash -lc \\
       'cd $APP_DIR && docker compose -f docker-compose.prod.yml --profile seed run --rm seed'
  3) sudo -u $DEPLOYER bash -lc \\
       'cd $APP_DIR && docker compose -f docker-compose.prod.yml up -d'
  4) Brauzerda http://YOUR_SERVER_IP/login — admin@nasiya.uz bilan kiring
     (parolni darhol o'zgartiring)

Domain qo'shilganda HTTPS:
  sudo certbot --nginx -d nasiya.uz -d www.nasiya.uz
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
