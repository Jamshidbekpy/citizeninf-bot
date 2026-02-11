from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards import district_keyboard, phone_keyboard, DISTRICTS
from app.states import AppealStates
from app.database import async_session_maker
from app.models import Appeal
from app.helpers import (
    PROMPT_FULL_NAME,
    PROMPT_PHONE,
    PROMPT_PROBLEM,
    ERR_DISTRICT_INVALID,
    ERR_PHONE_USE_BUTTON,
    ERR_PHONE_OWN_CONTACT,
    SUCCESS_APPEAL_SUBMITTED,
    normalize_phone,
    send_appeal_to_group,
)

router = Router()


@router.message(AppealStates.district, F.text.in_(DISTRICTS))
async def process_district(message: Message, state: FSMContext) -> None:
    await state.update_data(district=message.text)
    await state.set_state(AppealStates.full_name)
    await message.answer(PROMPT_FULL_NAME, reply_markup=None)


@router.message(AppealStates.district, F.text)
async def district_invalid(message: Message) -> None:
    await message.answer(ERR_DISTRICT_INVALID, reply_markup=district_keyboard())


@router.message(AppealStates.full_name, F.text)
async def process_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text.strip())
    await state.set_state(AppealStates.phone)
    await message.answer(PROMPT_PHONE, reply_markup=phone_keyboard())


@router.message(AppealStates.phone, F.contact)
async def process_phone(message: Message, state: FSMContext) -> None:
    if message.contact and message.contact.user_id != message.from_user.id:
        await message.answer(ERR_PHONE_OWN_CONTACT)
        return
    phone = message.contact.phone_number if message.contact else ""
    await state.update_data(phone=normalize_phone(phone))
    await state.set_state(AppealStates.problem)
    await message.answer(PROMPT_PROBLEM, reply_markup=None)


@router.message(AppealStates.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    await message.answer(ERR_PHONE_USE_BUTTON, reply_markup=phone_keyboard())


@router.message(AppealStates.problem, F.text)
async def process_problem(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    appeal = Appeal(
        user_id=message.from_user.id,
        full_name=data["full_name"],
        district=data["district"],
        phone=data["phone"],
        problem_text=message.text.strip(),
        is_active=True,
    )

    async with async_session_maker() as session:
        session.add(appeal)
        await session.commit()
        await session.refresh(appeal)

    group_message = await send_appeal_to_group(message.bot, appeal)
    if group_message:
        async with async_session_maker() as session:
            appeal_from_db = await session.get(Appeal, appeal.id)
            if appeal_from_db:
                appeal_from_db.group_message_id = group_message.message_id
                await session.commit()

    await message.answer(SUCCESS_APPEAL_SUBMITTED)
