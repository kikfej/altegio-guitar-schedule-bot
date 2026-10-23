# Altegio Guitar Schedule Bot

A lightweight Python service and Telegram bot designed to monitor guitar lesson schedules via the **Altegio REST API**, track booking changes (new, rescheduled, or cancelled lessons), and send automated reminders and notifications in **Telegram**.

## Features

- **Real-Time Schedule Viewing (`/schedule`)** — Fetches and formats current lesson bookings directly from the Altegio API.
- **Upcoming Lesson Reminders (`/upcoming`)** — Filters and displays lessons scheduled within the next 24 hours.
- **Change Detection (`/check` & Background Monitor)** — Compares live schedule data against a local JSON cache (`schedule_cache.json`) to detect newly added, rescheduled, or cancelled appointments.
- **Automated Background Polling** — Runs a dedicated background thread that periodically checks Altegio for updates and pushes instant alerts to the administrator's Telegram chat.
- **Built-in Demo Mode** — Automatically falls back to realistic sample data when Altegio API credentials are not configured, allowing instant local testing and demonstration.

## Project Structure

```text
.
├── bot.py             # Entry point: Telegram bot command handlers and background polling thread
├── altegio_api.py     # HTTP client for fetching booking records from the Altegio API (with demo fallback)
├── logic.py           # Core business logic: JSON caching, schedule diffing, date filtering, text formatting
├── config.py          # Environment variable loader and configuration settings
├── test_logic.py      # Unit test suite (pytest) covering core schedule logic
├── requirements.txt   # Project dependencies
├── .gitignore         # Git exclusion rules for secrets, cache, and virtual environments
└── README.md          # Project documentation
```

## Tech Stack

- **Python 3.10+**
- **pyTelegramBotAPI (`telebot`)** — Synchronous Telegram Bot API wrapper
- **Requests** — HTTP library for interacting with the Altegio REST API
- **python-dotenv** — Environment variable management from `.env` files
- **pytest** — Unit testing framework

## Quick Start (Copy & Paste)

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/altegio-guitar-schedule-bot.git](https://github.com/YOUR_USERNAME/altegio-guitar-schedule-bot.git)
cd altegio-guitar-schedule-bot
```

### 2. Create and Activate a Virtual Environment

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

**Linux / macOS:**
```bash
cat << 'EOF' > .env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CHAT_ID=your_telegram_chat_id_here
ALTEGIO_PARTNER_TOKEN=your_altegio_partner_token
ALTEGIO_USER_TOKEN=your_altegio_user_token
ALTEGIO_COMPANY_ID=111111
EOF
```

**Windows (PowerShell):**
```powershell
@"
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CHAT_ID=your_telegram_chat_id_here
ALTEGIO_PARTNER_TOKEN=your_altegio_partner_token
ALTEGIO_USER_TOKEN=your_altegio_user_token
ALTEGIO_COMPANY_ID=111111
"@ | Out-File -FilePath .env -Encoding utf8
```

> **Note:** To obtain a `TELEGRAM_BOT_TOKEN`, message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot`. To run the bot in **Demo Mode** without Altegio credentials, leave `ALTEGIO_PARTNER_TOKEN=your_altegio_partner_token` as is.

### 5. Run the Bot

```bash
python bot.py
```

## Usage Examples

Once the bot is running, open your bot in Telegram and use the following commands:

| Command | Description |
| :--- | :--- |
| `/start` or `/help` | Display welcome message and available commands |
| `/myid` | Get your personal Telegram Chat ID (to set as `ADMIN_CHAT_ID` in `.env`) |
| `/schedule` | Fetch and display the full guitar lesson schedule |
| `/upcoming` | Show lessons starting within the next 24 hours |
| `/check` | Manually check for schedule changes since the last snapshot |

**Example Output (`/schedule`):**
```text
🎸 Расписание уроков игры на гитаре:
1. 23.10.2026 в 14:00 — Алексей Смирнов (Электрогитара (индивидуальный урок))
2. 24.10.2026 в 15:00 — Мария Иванова (Акустическая гитара (разбор песен))
```

**Example Change Alert (`/check` or Auto-Notification):**
```text
🔔 Обнаружены изменения в расписании Altegio!

✅ Новые записи:
🎸 Расписание уроков игры на гитаре:
1. 25.10.2026 в 18:00 — Олег Петров (Укулеле)
```

## Running Tests

The core schedule diffing, caching, and filtering functions are covered by unit tests using `pytest`. Run the test suite with:

```bash
pytest -v
```