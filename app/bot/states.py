from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    language = State()


class Searching(StatesGroup):
    in_queue = State()
    in_call = State()
