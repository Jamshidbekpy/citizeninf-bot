from aiogram import Router

from app.handlers import start, appeal, admin_callback

router = Router()
router.include_router(start.router)
router.include_router(appeal.router)
router.include_router(admin_callback.router)
