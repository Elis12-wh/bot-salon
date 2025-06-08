import json
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class MainKeyboardText:
    texts = {
                "salon": "💅 О салоне красоты",
                "location": "📍 Адрес и проезд",
                "contact": "📞 Контактная информация",
                "faq": "❓ Вопросы и ответы",
                "appointment": "🔍 Онлайн-запись",
                "admin": "🔒 Панель администратора"  
        }


class AdminKeyboardText:
    texts = {
                "stats": "📊 Аналитика",
                "broadcast": "📢 Массовая рассылка",
                "rfaq": "❓ Управление FAQ",
                "back": "↩️ Вернуться"
        }

class FAQModerateKeyboardText:
    menu_texts = {
                "add": "➕ Создать новый вопрос",
                "remove": "➖ Удалить вопрос",
                "edit": "✏️ Изменить вопрос",
                "back": "↩️ Вернуться"
        }

    approve_delete_faq_texts = {
                "yes": "✅ Подтвердить",
                "no": "❌ Отменить"
        }
    
    edit_faq_texts = {
                "edit_question": "Изменить текст вопроса",
                "edit_answer": "Изменить текст ответа",
                "back": "↩️ Вернуться"
        }



# Состояния для разных операций с кнопками
class AddButtonStates(StatesGroup):
    waiting_for_button_text = State()
    waiting_for_reply = State()

class RemoveButtonStates(StatesGroup):
    waiting_for_button_text = State()

class EditButtonStates(StatesGroup):
    waiting_for_button_text = State()
    waiting_for_new_reply = State()

#Клавиатура для основных кнопок
class MainKeyboard:
    welcome_message_ru = (
        "👋 Добро пожаловать в Сладкие Кутикулы — место, где рождается красота и уют!\n\n"
        "✨ Почему выбирают нас?  \n✔ Профессиональные мастера с большим опытом  \n✔ Качественные материалы премиум-класса  \n✔ Уютная атмосфера и стерильные условия  \n✔ Широкий спектр услуг: маникюр, педикюр, покрытие, дизайн и не только  \nМы работаем, чтобы ваши ногти выглядели безупречно! 💖"
    )

    @staticmethod
    def get_main_keyboard(language: str = "ru", is_admin: bool = False) -> ReplyKeyboardMarkup:

        print(MainKeyboardText.texts.keys())
        
        keyboard = [
            [
                KeyboardButton(text=MainKeyboardText.texts["salon"]),
            ],
            [
                KeyboardButton(text=MainKeyboardText.texts["location"])
            ],
            [
                KeyboardButton(text=MainKeyboardText.texts["contact"])
            ],
            [
                KeyboardButton(text=MainKeyboardText.texts["faq"])
            ],
            [
                KeyboardButton(text=MainKeyboardText.texts["appointment"])
            ]
        ]
        if is_admin:
            keyboard.append([KeyboardButton(text=MainKeyboardText.texts["admin"])])

        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Клавиатура для админов
class AdminKeyboard:
    @staticmethod
    def get_admin_keyboard(language: str = "ru") -> ReplyKeyboardMarkup:
        
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=AdminKeyboardText.texts["stats"])],
                [KeyboardButton(text=AdminKeyboardText.texts["broadcast"])],
                [KeyboardButton(text=AdminKeyboardText.texts["rfaq"])],
                [KeyboardButton(text=AdminKeyboardText.texts["back"])]
            ],
            resize_keyboard=True
        )


class FAQModerateKeyboard:
    @staticmethod
    def get_faq_moderate_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardText.menu_texts["add"], callback_data="add_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.menu_texts["remove"], callback_data="remove_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.menu_texts["edit"], callback_data="edit_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.menu_texts["back"], callback_data="back_to_admin")]
            ]
        )

    @staticmethod
    def approve_delete_faq_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardText.approve_delete_faq_texts["yes"], callback_data="approve_delete_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.approve_delete_faq_texts["no"], callback_data="cancel_delete_faq")]
            ]
        )

    @staticmethod
    def chose_edit_action_faq_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardText.edit_faq_texts["edit_question"], callback_data="edit_question_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.edit_faq_texts["edit_answer"], callback_data="edit_answer_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardText.edit_faq_texts["back"], callback_data="back_to_admin")]
            ]
        )