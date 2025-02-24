from aiogram import Router

from app.handlers import commands, callbacks, text_handlers

router = Router()

router.include_router(commands.router)
router.include_router(callbacks.router)
router.include_router(text_handlers.router)