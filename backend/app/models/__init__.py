"""Re-export all models so Alembic autogenerate sees them."""

from app.models.audit import AdminAuditLog
from app.models.event import BotEvent
from app.models.feedback import Feedback
from app.models.product import NasiyaProduct
from app.models.provider import NasiyaProvider
from app.models.url_check import UrlCheckLog
from app.models.user import User

__all_models__ = [
    "NasiyaProvider",
    "NasiyaProduct",
    "User",
    "BotEvent",
    "AdminAuditLog",
    "UrlCheckLog",
    "Feedback",
]
