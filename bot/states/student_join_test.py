from aiogram.fsm.state import State, StatesGroup


class StudentJoinTestStates(StatesGroup):
    enter_code = State()
    y1_answers = State()
    y2_answers = State()
    open_bulk = State()
    confirm_submit = State()
