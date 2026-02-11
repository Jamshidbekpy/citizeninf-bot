from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.keyboards import district_keyboard
from app.states import AppealStates
from app.helpers import WELCOME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        WELCOME,
        reply_markup=district_keyboard(),
    )
    await state.set_state(AppealStates.district)
