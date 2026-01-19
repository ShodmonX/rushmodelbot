from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    choosing_role = State()
    entering_phone = State()
    entering_name = State()
