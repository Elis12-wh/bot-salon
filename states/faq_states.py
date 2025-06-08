from aiogram.fsm.state import StatesGroup, State

class FaqStates(StatesGroup):
    waiting_for_question = State()
