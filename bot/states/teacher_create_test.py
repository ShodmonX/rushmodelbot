from aiogram.fsm.state import State, StatesGroup


class TeacherCreateTestStates(StatesGroup):
    choose_template = State()
    enter_title = State()
    upload_material = State()
    enter_y1_key = State()
    enter_y2_key = State()
    enter_open_bulk = State()
    confirm_publish = State()
