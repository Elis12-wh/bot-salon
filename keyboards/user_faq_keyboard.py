from typing import Callable
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class UserFaqKeyboard: 
    @staticmethod
    async def get_keyboard(questions: list[str]) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=button_text)]
                for button_text in questions
            ],
            resize_keyboard=True,
        )
        return keyboard
