import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env в окружение программы
load_dotenv()

# Читаем секретные токены через метод словаря .get() (Лекция 3 и Лекция 14)
# Второй аргумент ("") — это значение по умолчанию, если переменная не найдена
TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID: str = os.environ.get("ADMIN_CHAT_ID", "")

ALTEGIO_PARTNER_TOKEN: str = os.environ.get("ALTEGIO_PARTNER_TOKEN", "")
ALTEGIO_USER_TOKEN: str = os.environ.get("ALTEGIO_USER_TOKEN", "")
ALTEGIO_COMPANY_ID: str = os.environ.get("ALTEGIO_COMPANY_ID", "")

# Режим демонстрации: если мы еще не вписали реальный токен Altegio,
# программа автоматически включит учебные данные, чтобы бот работал на защите!
USE_DEMO_MODE: bool = (
    not ALTEGIO_PARTNER_TOKEN 
    or ALTEGIO_PARTNER_TOKEN == "тут_будет_партнерский_токен"
)