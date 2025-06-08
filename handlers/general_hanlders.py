from aiogram import Router, types
from aiogram.filters import Command, CommandStart
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
from filters import NewUser
from states import FaqStates, UserStates


general_router = Router(name="general_router")


@general_router.message(NewUser(db), CommandStart())
async def start_handler_new_user(message: Message, state: FSMContext):
    user = await db.get_user(telegram_id=str(message.from_user.id))
    if user is None:
        await db.create_user(
            telegram_nickname=message.from_user.username or "no_username",
            first_name=message.from_user.first_name,
            telegram_id=str(message.from_user.id),
            language="ru",
            regularity=0
        )
    await message.answer("Привет!\nМы с тобой еще не знакомы - добро пожаловать в Сладкие Кутикулы - где рождается красота и уют!", reply_markup=keyboard)

# Обработчик команды /start
@general_router.message(CommandStart(), ~NewUser(db))
async def start_handler(message: Message, state: FSMContext, is_admin: bool = False):
    print("User id ", message.from_user.id)
    user = await db.get_user(telegram_id=str(message.from_user.id))
    keyboard = MainKeyboard.get_main_keyboard(user.language, is_admin)
          
    await message.answer("Выберите пункт меню или используйте команды для работы с ботом", reply_markup=keyboard)



@general_router.message(Command("help"))
async def help_handler(message: Message, state: FSMContext):
    answer = "ℹ️ Список доступных команд: \n\n"
    answer += "🔹 /start – Начать работу с ботом \n"
    answer += "🔹 /faq – Часто задаваемые вопросы \n"
    answer += "🔹 /appointment – Записаться на прием онлайн \n"
    answer += "📌 Выберите нужную команду или воспользуйтесь кнопками меню."
    await message.answer(answer)
    await state.clear()