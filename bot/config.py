import json
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Загрузка переменных окружения
if os.path.exists(os.path.join(BASE_DIR, '.env.local')):
    load_dotenv(os.path.join(BASE_DIR, '.env.local'))
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    LINK_CHANNEL = os.getenv('LINK_CHANNEL')
    # SHARE_LINK = os.getenv('SHARE_LINK')
    SHARE_LINK = 'https://t.me/+eS-fDtxBcV00YjMy'
    DB_URL = f"sqlite+aiosqlite:///{BASE_DIR}/db/{os.getenv('DB_NAME')}"
    # ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))
    ADMIN_IDS = ["@PolinaVasilkova", "@Pavlux29", "@K_A000003"]
    ADMIN_ID_NUMBER = [1895230640, 962582174]
    LOG_ROTATE_DAYS = int(os.getenv('LOG_ROTATE_DAYS', 15))
    SCHEDULER = os.getenv('SCHEDULER', 'False').lower() in ('true', '1', 'yes', 'on')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')