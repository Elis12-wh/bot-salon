from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.bot_config import ADMIN_IDS, FAQ_STORAGE_PATH
from keyboards import AdminKeyboard, MainKeyboard, FAQModerateKeyboard, UserFaqKeyboard
from aiogram.types import Message, CallbackQuery
from storage import db
from storage.db_handler import DBHandler
import aiosqlite
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils import FaqDataHandler
from states import AdminStates
from handlers.general_hanlders import start_handler

# Создаем роутер для админских команд
admin_router = Router(name="admin_router")

# Обработчик для кнопки "🔒 Админ панель"
@admin_router.message(lambda message: message.text in ["🔒 Панель администратора", "🔒 Administrator panel"] or message.text == "/admin")
async def handle_admin_panel(message: Message, state: FSMContext, is_admin: bool = False):
    print(f"DEBUG: message.text = {message.text!r}")
    if not is_admin:
        await message.answer(
            "У вас нет прав для доступа к панели администратора." if message.text == "🔒 Панель администратора" else "You don't have permission to access the administrator panel."
        )
        return
    # Получаем язык пользователя из БД, если нет - определяем по кнопке
    user = await db.get_user(telegram_id=str(message.from_user.id))
    if user and getattr(user, "language", None):
        language = user.language
    else:
        # Определяем язык по тексту кнопки
        if message.text == "🔒 Administrator panel":
            language = "en"
        else:
            language = "ru"
    keyboard = AdminKeyboard.get_admin_keyboard(language)
    await message.answer(
        "Панель администратора: доступные команды /stats \n/broadcast \n/admin" if language == "ru" else "Administrator panel: available commands /stats \n /broadcast \n/admin",
        reply_markup=keyboard
    )

@admin_router.message(lambda message: message.text == "↩️ Вернуться" or message.text == "↩️ Return")
async def handle_return_to_main(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    await state.clear()
    await start_handler(message, state, is_admin=True)

# Обработчик для кнопки "📊 Статистика"
@admin_router.message(lambda message: message.text in ["📊 Статистика", '/stats'])
async def handle_admin_statistics(message: Message, is_admin: bool = False):
    if not is_admin:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    # Получаем язык пользователя из БД, если нет - определяем по кнопке
    user = await db.get_user(telegram_id=str(message.from_user.id))
    if user and getattr(user, "language", None):
        language = user.language
    else:
        language = "en" if message.text == "📊 Statistics" else "ru"

    # Получаем общее количество пользователей
    total_users = len(await db.get_all_users())
    # Получаем количество новых пользователей за последнюю неделю
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    users = await db.get_all_users()
    new_users = sum(1 for user in users if user.date_joined >= one_week_ago)

    if language == "en":
        text = (
            f"👥 Total registered users: <b>{total_users}</b>\n"
            f"🆕 New registrations this week: <b>{new_users}</b>"
        )
    else:
        text = (
            f"👥 Всего зарегистрированных пользователей: <b>{total_users}</b>\n"
            f"🆕 Новых регистраций за неделю: <b>{new_users}</b>"
        )
    await message.answer(text, parse_mode="HTML")

MAX_CONCURRENT_SENDS = 20  # Одновременно не более 20 сообщений

async def send_message_safe(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
        return True
    except Exception:
        return False

@admin_router.message(lambda message: message.text in ["📢 Массовая рассылка", '/broadcast'])
async def handle_broadcast_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer(
            "У вас нет прав для выполнения этой команды."
        )
        return
    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await message.answer("Введите сообщение, которое хотите отправить всем пользователям.")

@admin_router.message(AdminStates.waiting_for_broadcast_text)
async def handle_broadcast_send(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer(
            "У вас нет прав для выполнения этой команды."
        )
        return

    users = await db.get_all_users()
    text = message.text

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SENDS)

    async def sem_send(user):
        async with semaphore:
            return await send_message_safe(message.bot, user.telegram_id, text)

    tasks = [sem_send(user) for user in users]
    results = await asyncio.gather(*tasks)
    count = sum(results)

    # Определяем язык для ответа админу
    user = await db.get_user(telegram_id=str(message.from_user.id))
    language = getattr(user, "language", None)
    if not language:
        language = "en" if message.text == "📢 Mass broadcast" else "ru"

    if language == "en":
        await message.answer(f"Broadcast completed successfully. Message delivered to {count} users.")
    else:
        await message.answer(f"Рассылка успешно завершена. Сообщение доставлено {count} пользователям.")
    await state.clear()

@admin_router.message(lambda message: message.text == "❓ Управление FAQ")
async def handle_faq_management(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer(
            "У вас нет прав для выполнения этой команды."
        )
        return
    reply_markup = FAQModerateKeyboard.get_faq_moderate_keyboard()
    await message.answer("Выберите действие для управления FAQ:", reply_markup=reply_markup)

@admin_router.callback_query(lambda c: c.data in ["add_faq", "remove_faq", "edit_faq"])
async def handle_faq_actions(callback: CallbackQuery, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await callback.answer("У вас нет прав для выполнения этой команды.")
        return
    if callback.data == 'add_faq':
        await callback.message.answer("Введите текст нового вопроса для FAQ")
        await state.set_state(AdminStates.waiting_for_new_faq_question)
    elif callback.data == 'remove_faq':
        faq_list = FaqDataHandler.get_questions(faq_path)
        keyboard = await UserFaqKeyboard.get_keyboard(faq_list)
        await callback.message.answer("Выберите вопрос, который хотите удалить из FAQ", reply_markup=keyboard)
        await state.set_state(AdminStates.waiting_for_remove_faq_question)
    elif callback.data == 'edit_faq':
        faq_list = FaqDataHandler.get_questions(faq_path)
        keyboard = await UserFaqKeyboard.get_keyboard(faq_list)
        await callback.message.answer("Выберите вопрос из FAQ, который хотите отредактировать", reply_markup=keyboard)
        await state.set_state(AdminStates.waiting_for_edit_faq)

@admin_router.message(AdminStates.waiting_for_new_faq_question)
async def handle_new_faq_question(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    await state.update_data(new_faq_question=message.text)
    await message.answer("Теперь введите текст ответа на этот вопрос")
    await state.set_state(AdminStates.waiting_for_new_faq_answer)

@admin_router.message(AdminStates.waiting_for_new_faq_answer)
async def handle_new_faq_answer(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    question = (await state.get_data())['new_faq_question']
    answer = message.text
    FaqDataHandler.add_question(faq_path, question, answer)
    await message.answer("Новый вопрос и ответ успешно добавлены в FAQ", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await handle_admin_panel(message, state, is_admin=True)

@admin_router.message(AdminStates.waiting_for_remove_faq_question)
async def handle_remove_faq_question(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    keyboard = FAQModerateKeyboard.approve_delete_faq_keyboard()
    await message.answer("Вы уверены, что хотите удалить этот вопрос из FAQ?\n\nЭто действие необратимо.", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_remove_faq_question_confirmation)
    await state.update_data(remove_faq_question=message.text)

@admin_router.callback_query(lambda c: c.data in ["approve_delete_faq", "cancel_delete_faq"])
async def handle_remove_faq_confirmation(callback: CallbackQuery, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await callback.answer("У вас нет прав для выполнения этой команды.")
        return
    if callback.data == "approve_delete_faq":
        question = (await state.get_data())['remove_faq_question']
        FaqDataHandler.remove_question(faq_path, question)
        await callback.message.answer("Вопрос успешно удален из FAQ", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    elif callback.data == "cancel_delete_faq":
        await state.clear()
        await handle_admin_panel(callback.message, state, is_admin=True)

@admin_router.message(AdminStates.waiting_for_edit_faq)
async def handle_edit_faq_selection(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    keyboard = FAQModerateKeyboard.chose_edit_action_faq_keyboard()
    await message.answer("Выберите, что хотите изменить:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_choose_edit_action_faq)
    await state.update_data(edit_faq_question=message.text, edit_faq_question_or_answer=None)

@admin_router.callback_query(lambda c: c.data in ["edit_question_faq", "edit_answer_faq"])
async def handle_edit_faq_choice(callback: CallbackQuery, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await callback.answer("У вас нет прав для выполнения этой команды.")
        return
    if callback.data == "edit_question_faq":
        await state.set_state(AdminStates.waiting_for_edit_faq_question)
        await callback.message.answer("Введите новый текст вопроса")
    elif callback.data == "edit_answer_faq":
        await state.set_state(AdminStates.waiting_for_edit_faq_answer)
        await callback.message.answer("Введите новый текст ответа")
    await state.update_data(edit_faq_question_or_answer=callback.data)

@admin_router.message(AdminStates.waiting_for_edit_faq_answer)
async def handle_edit_faq_answer(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    question = (await state.get_data())['edit_faq_question']
    answer = message.text
    FaqDataHandler.edit_answer(faq_path, question, answer)
    await message.answer("Ответ в FAQ успешно обновлен", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await handle_admin_panel(message, state, is_admin=True)

@admin_router.message(AdminStates.waiting_for_edit_faq_question)
async def handle_edit_faq_question(message: Message, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    question = (await state.get_data())['edit_faq_question']
    new_question = message.text
    FaqDataHandler.edit_question(faq_path, question, new_question)
    await message.answer("Вопрос в FAQ успешно обновлен", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await handle_admin_panel(message, state, is_admin=True)

@admin_router.callback_query(lambda c: c.data == "back_to_admin")
async def handle_return_to_admin(callback: CallbackQuery, state: FSMContext, is_admin: bool, faq_path: str):
    if not is_admin:
        await callback.answer("У вас нет прав для выполнения этой команды.")
        return
    await state.clear()
    await handle_admin_panel(callback.message, state, is_admin=True)
