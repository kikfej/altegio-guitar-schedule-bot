import os
from dotenv import load_dotenv

# Load environment variables from the .env file into os.environ
load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN_CHAT_ID: str = os.environ.get("ADMIN_CHAT_ID", "").strip()

ALTEGIO_PARTNER_TOKEN: str = os.environ.get("ALTEGIO_PARTNER_TOKEN", "").strip()
ALTEGIO_USER_TOKEN: str = os.environ.get("ALTEGIO_USER_TOKEN", "").strip()
ALTEGIO_COMPANY_ID: str = os.environ.get("ALTEGIO_COMPANY_ID", "").strip()

# Enable demo mode automatically if Altegio credentials are missing or use placeholders
USE_DEMO_MODE: bool = (
    not ALTEGIO_PARTNER_TOKEN
    or ALTEGIO_PARTNER_TOKEN.startswith("тут_")
    or ALTEGIO_PARTNER_TOKEN.startswith("your_")
)