from aiogram.fsm.state import State, StatesGroup


class AdminOnboardingStates(StatesGroup):
    entering_phone = State()
    entering_name = State()
