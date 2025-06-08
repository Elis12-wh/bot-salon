from storage.db_handler import DBHandler
from config.bot_config import DB_PATH
import asyncio

db = DBHandler() 
asyncio.run(db.init(DB_PATH))
