from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.keyboards import district_keyboard, start_appeal_inline
from app.states import AppealStates
from app.helpers import START_INSTRUCTION, PROMPT_DISTRICT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        START_INSTRUCTION,
        reply_markup=start_appeal_inline(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "start_appeal")
async def callback_start_appeal(callback: CallbackQuery, state: FSMContext) -> None:
    """«Murojaat qilish» bosilganda — tuman tanlash bosqichiga o‘tadi."""
    await state.set_state(AppealStates.district)
    await callback.message.answer(
        PROMPT_DISTRICT,
        reply_markup=district_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
