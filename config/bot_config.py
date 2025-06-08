from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = eval(os.getenv("ADMIN_IDS"))
FAQ_STORAGE_PATH = os.getenv("FAQ_STORAGE_PATH")
DB_PATH = os.getenv("DB_PATH")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


