# Nasiya Aggregator

O'zbekistondagi nasiya (BNPL/muddatli to'lov) xizmatlarini bir joyga yig'uvchi Telegram bot + web dashboard.

## Nima muammoni yechadi?

O'zbekistonda 7–10 ta katta nasiya provayderi mavjud (Alif, Uzum, IMAN, TBC, Anorbank, ZoodPay va h.k.) — ularning har birining turli limitlari, muddatlari va shartlari bor. Foydalanuvchilar hozir har bir ilovaga alohida kirib tekshirishga majbur. Bu loyiha ularni **rasmiy manbalardan tasdiqlangan** holda bir joyga to'playdi.

## Asosiy tamoyillar

- **Faqat rasmiy manbalar** — har bir ma'lumot provayder rasmiy sayti / CBU registri / rasmiy App Store listing'iga bog'lanadi. Uchinchi tomon blog/news qabul qilinmaydi.
- **Audit tekshirish** — har 90 kunda rasmiy link'lar avtomat tekshiriladi, admin ko'rib chiqadi.
- **Ochiq source trail** — har bir maydon qaysi URL'dan olinganini foydalanuvchi ham ko'ra oladi.

## Texnologik stek

| Qatlam | Texnologiya |
|---|---|
| Backend API | FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic |
| Bot | aiogram 3.x |
| Frontend | Next.js 14 + shadcn/ui + Tremor + TanStack Query |
| DB | PostgreSQL 16 + Redis 7 |
| Python package manager | **uv** |
| Tillar | UZ / RU / EN |

## Dastlabki sozlash

### 1. `uv` o'rnatish (agar yo'q bo'lsa)

```bash
# Rasmiy installer
curl -LsSf https://astral.sh/uv/install.sh | sh
# yoki
brew install uv
```

### 2. `.env` fayl yaratish

```bash
cp .env.example .env
# .env ochib: SECRET_KEY, BOT_TOKEN, BOT_ADMIN_IDS to'ldiring
# SECRET_KEY uchun:
openssl rand -hex 32
```

### 3. Bog'liqliklarni o'rnatish

```bash
make install
```

### 4. Infrastrukturani ko'tarish

```bash
make up           # Postgres + Redis docker'da ishga tushadi
make migrate      # Alembic migratsiyalari
make seed         # 7 ta tasdiqlangan provayderni DB'ga yuklash
```

### 5. Servislarni ishga tushirish

Uchta terminal kerak:

```bash
make backend      # FastAPI  → http://localhost:8000  (/docs da Swagger)
make bot          # Telegram bot (BOT_TOKEN bo'lishi shart)
make dashboard    # Next.js  → http://localhost:3000
```

## Loyiha strukturasi

```
nasiya/
├── backend/           FastAPI API + Alembic
├── bot/               aiogram 3 Telegram bot
├── dashboard/         Next.js 14 admin UI
├── docs/
│   └── sources.md     Rasmiy manbalar registri
├── docker-compose.yml Postgres + Redis
├── Makefile           Qisqa shortcut'lar
└── .env.example
```

## Litsenziya va ma'lumot javobgarligi

Bu bot — **ma'lumot agregatori**. Yakuniy nasiya shartlari har doim provayderning rasmiy manbasida. Botdagi har bir kartochkada oxirgi tekshirish sanasi ko'rsatiladi.

Manbalar ro'yxati: [`docs/sources.md`](docs/sources.md).
