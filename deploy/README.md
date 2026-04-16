# Nasiya Aggregator — Production Deploy Yo'riqnomasi

Bu hujjat — toza Ubuntu 22.04/24.04 server'ga loyihani **birinchi marta** o'rnatish va **keyingi marta yangilash** uchun.

---

## 0. Talablar

- Ubuntu 22.04 yoki 24.04 (Debian-based ham bo'ladi)
- 2 GB RAM minimum (4 GB tavsiya — Postgres + Redis + 3 ta servis)
- 10 GB bo'sh disk
- Root yoki sudo huquqlar
- Server'ning ochiq IP manzili (yoki domain)
- Telegram bot token ([@BotFather](https://t.me/BotFather)'dan)

---

## 1. Birinchi marta — server bootstrap

### Server'ga SSH bilan kiring (root sifatida)

```bash
ssh root@YOUR_SERVER_IP
```

### Bootstrap skriptini ishga tushiring

Skript hammasini avtomat qiladi: docker, nginx, firewall, deployer foydalanuvchi, repo klon, nginx config.

```bash
curl -fsSL https://raw.githubusercontent.com/Khasan712/nasiya-aggregator/main/deploy/scripts/server_init.sh | bash
```

> **Qayd:** Yoki repo'ni qo'lda klon qiling va skriptni mahalliy ishga tushiring:
> ```bash
> git clone https://github.com/Khasan712/nasiya-aggregator.git /opt/nasiya
> bash /opt/nasiya/deploy/scripts/server_init.sh
> ```

### `.env` faylini to'ldiring

```bash
cd /opt/nasiya
nano .env
```

`__CHANGE_ME__` qiymatlari:

| O'zgaruvchi | Qiymat |
|---|---|
| `POSTGRES_PASSWORD` | `openssl rand -base64 32` natijasi |
| `DATABASE_URL` va `DATABASE_URL_SYNC` | parolni xuddi shunday qo'ying |
| `SECRET_KEY` | `openssl rand -hex 32` |
| `SERVICE_TOKEN` va `DASHBOARD_SERVICE_TOKEN` | `openssl rand -hex 24` (bir xil!) |
| `BOT_TOKEN` | @BotFather'dan |
| `BOT_ADMIN_IDS` | sizning Telegram ID'ingiz ([@userinfobot](https://t.me/userinfobot)) |
| `CORS_ORIGINS` | `http://YOUR_SERVER_IP` |
| `NEXT_PUBLIC_BACKEND_URL` | `http://YOUR_SERVER_IP` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | login uchun |

### Database'ni seed qiling (faqat birinchi marta)

```bash
sudo -u deployer bash -lc 'cd /opt/nasiya && \
  docker compose -f docker-compose.prod.yml --profile seed run --rm seed'
```

Bu: Alembic migratsiyalarini qo'llaydi, 15 ta provayderni yuklaydi, admin foydalanuvchini yaratadi.

### Servislarni ishga tushiring

```bash
sudo -u deployer bash -lc 'cd /opt/nasiya && \
  docker compose -f docker-compose.prod.yml up -d'
```

### Tekshiring

```bash
# Container statuslari (5 ta servis healthy bo'lishi kerak)
docker ps

# Backend
curl http://127.0.0.1:8000/api/v1/health

# Dashboard (login sahifaga 200 qaytaradi, /admin → 307 redirect)
curl -I http://127.0.0.1:3000/login

# Public access (nginx orqali)
curl http://YOUR_SERVER_IP/api/v1/health
curl -I http://YOUR_SERVER_IP/login
```

Brauzerda **http://YOUR_SERVER_IP/login** → admin login (avval kiritgan email/parol).

Telegram'da bot — `/start` → 15 ta xizmat ro'yxati.

---

## 2. Keyingi marta — yangilanish

Code yangilanishidan so'ng (yangi commit'lar `main` branch'da):

```bash
ssh deployer@YOUR_SERVER_IP
cd /opt/nasiya
./deploy/scripts/deploy.sh
```

Skript:
1. `git pull origin main`
2. Docker images'ni qayta build qiladi (faqat o'zgargan layerlar)
3. Yangi migratsiyalarni qo'llaydi
4. Servislarni rolling restart qiladi
5. Status va so'nggi loglar ko'rsatadi

---

## 3. Backup (kunlik avtomat)

`crontab -e` (deployer foydalanuvchisi sifatida):

```cron
0 3 * * * /opt/nasiya/deploy/scripts/backup.sh >> /opt/nasiya/backups/backup.log 2>&1
```

Har kuni 03:00 da `/opt/nasiya/backups/nasiya_YYYYMMDD_HHMMSS.sql.gz` yaratiladi va 30 kundan eski fayllar avtomat o'chiriladi.

### Backup'dan tiklash

```bash
gunzip -c /opt/nasiya/backups/nasiya_YYYYMMDD.sql.gz | \
  docker exec -i nasiya-postgres psql -U nasiya -d nasiya
```

---

## 4. Logs va debugging

```bash
cd /opt/nasiya

# Hammasi
docker compose -f docker-compose.prod.yml logs --tail 100 -f

# Bitta servis
docker compose -f docker-compose.prod.yml logs --tail 100 -f backend
docker compose -f docker-compose.prod.yml logs --tail 100 -f bot
docker compose -f docker-compose.prod.yml logs --tail 100 -f dashboard

# Konteyner ichiga kirish
docker exec -it nasiya-backend bash
docker exec -it nasiya-postgres psql -U nasiya -d nasiya
```

### Migratsiya muammosi

```bash
# Hozirgi versiyani ko'rish
docker compose -f docker-compose.prod.yml run --rm backend alembic current

# Bitta orqaga
docker compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1
```

---

## 5. Portlarni o'zgartirish (server'da boshqa loyihalar bilan to'qnashganda)

Default'da loyiha host'da `127.0.0.1:8000` (backend) va `127.0.0.1:3000` (dashboard) portlarini ishlatadi. Agar serverdagi boshqa loyihalar shu portlarni band qilgan bo'lsa, `.env` faylda yangi portlar yozing:

```bash
nano /opt/nasiya/.env
# qo'ying yoki o'zgartiring:
BACKEND_HOST_PORT=18000
DASHBOARD_HOST_PORT=13000
```

So'ng deploy:

```bash
cd /opt/nasiya
./deploy/scripts/deploy.sh   # build + restart + nginx config'ni avtomat render qiladi
```

`deploy.sh` `render_nginx.sh`'ni chaqiradi — u `.env`'dagi yangi portlarni o'qib, `/etc/nginx/conf.d/nasiya.conf`'ni qayta yozadi va nginx'ni reload qiladi. Faqat config haqiqatan o'zgargan bo'lsa reload bo'ladi (idempotent).

**Container ichidagi portlar** (Postgres 5432, Redis 6379, backend 8000, dashboard 3000) doim default qoladi — Docker tarmog'i ichida ular standart raqamlar bilan ishlaydi.

---

## 6. Domain qo'shish (keyinchalik)

Domain DNS A-record'ni server IP'ga yo'naltirgandan so'ng:

```bash
sudo certbot --nginx -d nasiya.uz -d www.nasiya.uz
```

Certbot avtomat HTTPS sertifikat oladi va nginx config'ni HTTPS uchun yangilaydi.

`.env` faylida ham yangilang:
- `CORS_ORIGINS=https://nasiya.uz,https://www.nasiya.uz`
- `NEXT_PUBLIC_BACKEND_URL=https://nasiya.uz`

So'ng:
```bash
docker compose -f docker-compose.prod.yml restart backend dashboard
```

---

## 7. Xavfsizlik

- ✅ Postgres va Redis docker tarmog'idan tashqariga ko'rinmaydi
- ✅ Backend va dashboard portlari faqat `127.0.0.1` ga bog'langan (nginx orqali)
- ✅ UFW firewall: faqat 22 (SSH), 80 (HTTP), 443 (HTTPS) ochiq
- ✅ Nginx login endpoint'iga rate limit (10 r/min)
- ✅ Server token hash'lari production'da minimum uzunlik tekshiriladi (boot'da fail-fast)
- ✅ Production'da Swagger/OpenAPI yashirin (404)

### Tavsiyalar

- SSH parol bilan kirishni o'chirib, faqat key bilan kirish: `/etc/ssh/sshd_config` da `PasswordAuthentication no`
- Ko'k yoq foydalanuvchi (root SSH) o'chirish
- `fail2ban` o'rnatish (qo'shimcha brute-force himoyasi)
- `unattended-upgrades` paket — security patchlar avtomat

---

## 8. Tez-tez beriladigan savollar

**Q: Bot ishlamayapti, nima qilish kerak?**
A: `BOT_TOKEN` to'g'rimi tekshiring (`docker logs nasiya-bot`). Token yo'q yoki noto'g'ri bo'lsa, `nano .env` ichida tuzating va `docker compose -f docker-compose.prod.yml restart bot`.

**Q: "Sinmagan URL" xabarlarini olmayapman**
A: `BOT_ADMIN_IDS` da Telegram numeric ID'ingiz (raqam) borligini tekshiring. Username (`@username`) emas — son ([@userinfobot](https://t.me/userinfobot)).

**Q: Dashboard'da xato yoki bo'sh sahifalar**
A: `DASHBOARD_SERVICE_TOKEN` va `SERVICE_TOKEN` aynan **bir xil** bo'lishi kerak. Tekshirish: `docker logs nasiya-dashboard --tail 50`.

**Q: "service_token missing" xato bilan backend ishga tushmayapti**
A: Production safety check ishladi. `.env` da `SERVICE_TOKEN` va `SECRET_KEY` belgilanganini tekshiring.

**Q: Servisni vaqtincha to'xtatish**
A: `docker compose -f docker-compose.prod.yml stop` (data saqlanadi). Qayta yoqish: `start`.

**Q: Hammasi barbod bo'ldi, qaytadan boshlash**
A: `docker compose -f docker-compose.prod.yml down -v` (⚠ **`-v` volumeni ham o'chiradi — DB yo'qoladi!**). Backup'dan tiklash uchun yuqoridagi 3-bo'limga qarang.
