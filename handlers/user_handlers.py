from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.bot_config import ADMIN_IDS, FAQ_STORAGE_PATH, GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID
from keyboards import AdminKeyboard, MainKeyboard, FAQModerateKeyboard, UserFaqKeyboard
from aiogram.types import Message, CallbackQuery
from storage import db
import aiosqlite
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils import FaqDataHandler
from filters import VipUser
from services import GoogleSheetsManager
from states import FaqStates, UserStates
from keyboards import MainKeyboardText
from handlers.general_hanlders import start_handler


user_router = Router(name="user_router")
google_sheets = GoogleSheetsManager(
    creds_path=GOOGLE_CREDENTIALS_PATH,
    spreadsheet_id=SPREADSHEET_ID
)


@user_router.message(lambda message: message.text == MainKeyboardText.texts.get("faq") or message.text == "/faq")
async def handle_faq_menu(message: Message, state: FSMContext):
    questions = FaqDataHandler.get_questions(FAQ_STORAGE_PATH)
    keyboard = await UserFaqKeyboard.get_keyboard(questions)
    answer = "Пожалуйста, выберите интересующий вас вопрос:"
    await message.answer(answer, reply_markup=keyboard)
    await state.set_state(FaqStates.waiting_for_question)

@user_router.message(FaqStates.waiting_for_question)
async def handle_faq_answer(message: Message, state: FSMContext, is_admin: bool = False):
    question = message.text
    answer = FaqDataHandler.get_answer(FAQ_STORAGE_PATH, question)
    if not answer:
        await state.clear()
        await start_handler(message, state, is_admin)
        return
    await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@user_router.message(lambda message: message.text == "💅 О салоне красоты")
async def handle_about_salon(message: Message, state: FSMContext):
    text = "Добро пожаловать в Сладкие Кутикулы - место, где рождается красота и уют!\n\n ✨ Почему выбирают нас?  \n✔ Профессиональные мастера с большим опытом  \n✔ Качественные материалы премиум-класса  \n✔ Уютная атмосфера и стерильные условия  \n✔ Широкий спектр услуг: маникюр, педикюр, покрытие, дизайн и не только  \nМы работаем, чтобы ваши ногти выглядели безупречно! 💖"
    await message.answer(text)
    await state.clear()


@user_router.message(lambda message: message.text == "📍 Адрес и проезд")
async def handle_directions(message: Message, state: FSMContext):
    text = "Наш адрес: \nг. Москва, ул. Тверская, д. 10, 3 этаж, ТЦ \"Стиль\".\n\n"
    text += "🚗 На автомобиле: \n• Удобный въезд с ул. Тверской \n• Бесплатная парковка в ТЦ (первые 2 часа) \n• Ищите вывеску салона «Nail Art» у главного входа\n\n"
    text += "🚇 На общественном транспорте: \n• Станция метро «Тверская» (5 минут пешком) \n• Автобусы: №№ 101, 904 (остановка «Тверская площадь») \n• От метро следуйте прямо до ТЦ «Стиль», вход через стеклянные двери"
    await message.answer(text)
    await state.clear()


@user_router.message(lambda message: message.text == "📞 Контактная информация" or message.text == "/contacts")
async def handle_contact_info(message: Message, state: FSMContext):
    text = "📞 Наши контакты:  \n💬 Телефон: +7 (925) 478-32-15  \n📩 Email: beauty.nails@mail.ru  \n📱 Instagram: @glamour_nails_spb  \n🌐 Сайт: glamour-nails.ru"
    await message.answer(text)
    await state.clear()


@user_router.message(lambda message: message.text == "🔍 Онлайн-запись" or message.text == "/appointment")
async def handle_appointment_start(message: Message, state: FSMContext):
    workers = await google_sheets.get_worker_names()
    keyboard = await UserFaqKeyboard.get_keyboard(workers)
    await message.answer("Пожалуйста, выберите мастера для записи:", reply_markup=keyboard)
    await state.set_state(UserStates.picking_worker)


@user_router.message(lambda message: message.text == "🔍 Онлайн-запись" or message.text == "/appointment", VipUser(db))
async def handle_vip_appointment_start(message: Message, state: FSMContext):
    workers = await google_sheets.get_worker_names()
    keyboard = await UserFaqKeyboard.get_keyboard(workers)
    await message.answer("Благодарим за постоянное доверие! Выберите, пожалуйста, мастера:", reply_markup=keyboard)
    await state.set_state(UserStates.picking_worker)


@user_router.message(UserStates.picking_worker)
async def handle_worker_selection(message: Message, state: FSMContext):
    worker_windows = await google_sheets.get_worker_windows(message.text)
    await state.update_data(worker_windows=worker_windows)
    dates = worker_windows.get_dates()
    keyboard = await UserFaqKeyboard.get_keyboard(dates)
    await message.answer("Выберите удобную дату:", reply_markup=keyboard)
    await state.set_state(UserStates.picking_date)


@user_router.message(UserStates.picking_date)
async def handle_date_selection(message: Message, state: FSMContext):
    date = message.text
    worker_windows = await state.get_data()
    await state.update_data(date=date)
    windows = worker_windows.get("worker_windows").get_windows(date)
    keyboard = await UserFaqKeyboard.get_keyboard(windows)
    await message.answer("Выберите удобное время:", reply_markup=keyboard)
    await state.set_state(UserStates.picking_time)


@user_router.message(UserStates.picking_time)
async def handle_time_selection(message: Message, state: FSMContext):
    time = message.text
    date = (await state.get_data())["date"]
    worker_windows = (await state.get_data())["worker_windows"]
    worker_name = worker_windows.worker_name
    await google_sheets.reserve_window(message.from_user.first_name, worker_name, date, time)
    await message.answer(f"Отлично! Ваша запись подтверждена на {date} в {time}. Вас будет ждать мастер {worker_name}", reply_markup=types.ReplyKeyboardRemove())
    for admin in ADMIN_IDS:
        await message.bot.send_message(admin, f"Новая запись:\nКлиент: {message.from_user.first_name}\nДата: {date}\nВремя: {time}\nМастер: {worker_name}\n\nКонтактная информация:\nID: {message.from_user.id}\nUsername: {message.from_user.username}")
    await state.clear()

