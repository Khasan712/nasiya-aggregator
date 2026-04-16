from aiogram import Router

from app.handlers import common, feedback, lang, start

router = Router()
router.include_router(start.router)
router.include_router(lang.router)
router.include_router(common.router)
# Feedback router is included LAST because its catch-all F.text handler is
# guarded by the "awaiting feedback" Redis flag, but we still want all the
# more specific handlers above to win.
router.include_router(feedback.router)
