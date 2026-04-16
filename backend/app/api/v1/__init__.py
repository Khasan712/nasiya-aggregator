"""v1 API router aggregation."""

from fastapi import APIRouter

from app.api.v1 import admin, auth, bot, feedback, health, products, providers, stats, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(providers.router)
api_router.include_router(products.router)
api_router.include_router(bot.router)
api_router.include_router(stats.router)
api_router.include_router(admin.router)
api_router.include_router(users.router)
api_router.include_router(feedback.router)
