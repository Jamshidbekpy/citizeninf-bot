"""
Appeal delivery: send appeal notification to admin group.
"""

from aiogram import Bot

from app.config import config
from app.models import Appeal
from app.keyboards import appeal_done_inline
from app.helpers.text import format_appeal_notify


async def send_appeal_to_group(bot: Bot, appeal: Appeal) -> object | None:
    """Send formatted appeal to admin group with inline 'done' button. Returns sent Message."""
    text = format_appeal_notify(appeal)
    msg = await bot.send_message(
        config.GROUP_ID,
        text,
        reply_markup=appeal_done_inline(appeal.id),
        parse_mode="HTML",
    )
    return msg
