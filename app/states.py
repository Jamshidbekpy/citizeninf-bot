from aiogram.fsm.state import State, StatesGroup


class AppealStates(StatesGroup):
    district = State()
    full_name = State()
    phone = State()
    problem = State()
