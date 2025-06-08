from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_question = State()
    picking_worker = State()
    picking_date = State()
    picking_time = State()