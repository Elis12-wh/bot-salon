from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Обработчик для рассылки
class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_new_faq_question = State()
    waiting_for_new_faq_answer = State()
    waiting_for_remove_faq_question = State()
    waiting_for_edit_faq_question = State()
    waiting_for_remove_faq_question_confirmation = State()
    waiting_for_choose_edit_action_faq = State()
    waiting_for_edit_faq_question = State()
    waiting_for_edit_faq_answer = State()
    waiting_for_edit_faq = State()