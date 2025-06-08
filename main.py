from config.bot_config import BOT_TOKEN, ADMIN_IDS, FAQ_STORAGE_PATH, DB_PATH
from storage import db
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, Message
import asyncio
import logging
import aiosqlite
from handlers import admin_router, user_router, general_router
from keyboards.user_faq_keyboard import UserFaqKeyboard
from utils.faq_data_handler import FaqDataHandler
from states import FaqStates, UserStates
from services import GoogleSheetsManager
from middlewares.admin_middlewares import AdminCheckMiddleware
from filters import NewUser
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats
from aiogram.types import BotCommandScopeChat, BotCommandScopeChatMember
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

aiogram_logger = logging.getLogger("aiogram")
aiogram_logger.setLevel(logging.INFO)


user_commands = [
    BotCommand(command="start", description="start and menu"),
    BotCommand(command="faq", description="questions and answers"),
    BotCommand(command="appointment", description="book an appointment"),
    BotCommand(command="help", description="help"),
    BotCommand(command="contacts", description="contacts")
]

async def setup_bot_commands(bot: Bot):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeAllPrivateChats())


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(AdminCheckMiddleware(ADMIN_IDS, FAQ_STORAGE_PATH))
dp.callback_query.middleware(AdminCheckMiddleware(ADMIN_IDS, FAQ_STORAGE_PATH))


# Подключаем роутеры
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(general_router)


async def main(): 
    await db.init(DB_PATH)
    try:
        # Запуск бота
        logging.info("Starting bot...")
        await setup_bot_commands(bot)
        await dp.start_polling(bot)
    finally:
        # Корректное завершение
        await bot.session.close()
        await db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())