from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.database import async_session_maker
from app.models import Appeal
from app.helpers import (
    APPEAL_NOT_FOUND,
    APPEAL_DONE_ALREADY,
    APPEAL_DONE_CONFIRM,
    format_appeal_reviewed,
    get_reviewer_display_name,
)
from app.logging_config import get_logger
from app.metrics import CALLBACKS_DONE

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery) -> None:
    appeal_id = int(callback.data.split(":", 1)[1])
    async with async_session_maker() as session:
        appeal = await session.get(Appeal, appeal_id)
        if not appeal:
            try:
                await callback.answer(APPEAL_NOT_FOUND, show_alert=True)
            except TelegramBadRequest as e:
                logger.warning("callback_answer_failed", appeal_id=appeal_id, error=str(e))
            return
        if not appeal.is_active:
            try:
                await callback.answer(APPEAL_DONE_ALREADY)
            except TelegramBadRequest as e:
                logger.warning("callback_answer_failed", appeal_id=appeal_id, error=str(e))
            return
        appeal.is_active = False
        appeal.reviewed_by = callback.from_user.id if callback.from_user else None
        await session.commit()

    CALLBACKS_DONE.inc()
    logger.info(
        "callback_done",
        appeal_id=appeal_id,
        reviewed_by=appeal.reviewed_by,
    )

    # Xabarni o‘chirmaymiz, edit qilamiz: tepaga "ko‘rib chiqildi" qatorini qo‘shamiz
    user = callback.from_user
    reviewer_name = get_reviewer_display_name(
        user.first_name if user else None,
        user.last_name if user else None,
    )
    new_text = format_appeal_reviewed(appeal, reviewer_name)
    try:
        await callback.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")
    except Exception as e:
        logger.warning("edit_message_failed", appeal_id=appeal_id, error=str(e))
    try:
        await callback.answer(APPEAL_DONE_CONFIRM)
    except TelegramBadRequest as e:
        logger.warning("callback_answer_failed", appeal_id=appeal_id, error=str(e))
