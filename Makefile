.PHONY: help up down logs backend bot dashboard migrate revision seed install clean \
        prod-build prod-up prod-down prod-logs prod-migrate prod-seed prod-deploy

help:
	@echo "Nasiya project — make targets:"
	@echo "  make install    Install all Python + Node dependencies"
	@echo "  make up         Start Postgres + Redis (docker)"
	@echo "  make down       Stop Postgres + Redis"
	@echo "  make logs       Tail infra logs"
	@echo "  make backend    Run FastAPI dev server (port 8000)"
	@echo "  make bot        Run Telegram bot"
	@echo "  make dashboard  Run Next.js dashboard (port 3000)"
	@echo "  make migrate    Apply Alembic migrations"
	@echo "  make revision m='msg'  Create new Alembic revision"
	@echo "  make seed       Seed verified nasiya providers"

install:
	cd backend && uv sync
	cd bot && uv sync
	cd dashboard && npm install

up:
	docker compose up -d
	@echo "Postgres: localhost:5433  |  Redis: localhost:6380"

down:
	docker compose down

logs:
	docker compose logs -f

backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

bot:
	cd bot && uv run python -m app.main

dashboard:
	cd dashboard && npm run dev

migrate:
	cd backend && uv run alembic upgrade head

revision:
	cd backend && uv run alembic revision --autogenerate -m "$(m)"

seed:
	cd backend && uv run python -m app.scripts.seed_providers

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# ─── Production (docker-compose.prod.yml) ─────────────────────────────────

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs --tail 100 -f

prod-migrate:
	docker compose -f docker-compose.prod.yml --profile migrate run --rm migrate

prod-seed:
	docker compose -f docker-compose.prod.yml --profile seed run --rm seed

prod-deploy:
	./deploy/scripts/deploy.sh
