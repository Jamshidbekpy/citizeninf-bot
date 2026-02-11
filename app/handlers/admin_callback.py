from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database import async_session_maker
from app.models import Appeal
from app.helpers import (
    APPEAL_NOT_FOUND,
    APPEAL_DONE_ALREADY,
    APPEAL_DONE_CONFIRM,
)

router = Router()


@router.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery) -> None:
    appeal_id = int(callback.data.split(":", 1)[1])
    async with async_session_maker() as session:
        appeal = await session.get(Appeal, appeal_id)
        if not appeal:
            await callback.answer(APPEAL_NOT_FOUND, show_alert=True)
            return
        if not appeal.is_active:
            await callback.answer(APPEAL_DONE_ALREADY)
            try:
                await callback.message.delete()
            except Exception:
                pass
            return
        appeal.is_active = False
        await session.commit()

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer(APPEAL_DONE_CONFIRM)
