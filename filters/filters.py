from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils import FaqDataHandler
from services import GoogleSheetsManager
from aiogram.fsm.context import FSMContext

class NewUser(BaseFilter):
    def __init__(self, db):
        self.database = db
    
    async def __call__(self, message: Message) -> bool:
        user = await self.database.get_user(telegram_id=str(message.from_user.id))
        return user is None


class VipUser(BaseFilter):
    def __init__(self, source_path):
        self.source_path = source_path
    
    async def __call__(self, message: Message, db) -> bool:
        user_id = message.from_user.id
        regularity = await db.get_user_regularity(telegram_id=str(user_id))
        return regularity > 5
