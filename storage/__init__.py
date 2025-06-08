from .db_handler import DBHandler
from .online_db import db

db = DBHandler()

__all__ = ['DBHandler', 'db'] 