import threading
import time
import telebot

import config
import altegio_api
import logic

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


def build_changes_report() -> str | None:
    """
    Fetch current schedule, compare it with cached data, update the cache,
    and return a formatted change report (or None if nothing changed).
    """
    new_lessons = altegio_api.fetch_lessons_from_altegio()
    if not new_lessons:
        return None

    old_lessons = logic.load_saved_schedule()
    changes = logic.find_schedule_changes(old_lessons, new_lessons)
    logic.save_schedule(new_lessons)

    if not old_lessons:
        return None

    added = changes["added"]
    cancelled = changes["cancelled"]
    rescheduled = changes["rescheduled"]

    if not added and not cancelled and not rescheduled:
        return None

    report_lines: list[str] = ["🔔 Обнаружены изменения в расписании Altegio!"]

    if added:
        report_lines.append("\n✅ Новые записи:")
        report_lines.append(logic.format_schedule_text(added))
    if rescheduled:
        report_lines.append("\n🔄 Перенесенные уроки:")
        report_lines.append(logic.format_schedule_text(rescheduled))
    if cancelled:
        report_lines.append("\n❌ Отмененные уроки:")
        report_lines.append(logic.format_schedule_text(cancelled))

    return "\n".join(report_lines)


@bot.message_handler(commands=["start", "help"])
def handle_start(message: telebot.types.Message) -> None:
    """Send welcome message and command list."""
    mode_note = (
        "\n⚠️ Сейчас включен Демо-режим (учебные данные)."
        if config.USE_DEMO_MODE
        else ""
    )
    welcome_text = (
        "Привет! Я бот мониторинга расписания уроков гитары (Altegio).\n\n"
        "Доступные команды:\n"
        "/schedule — показать все расписание уроков\n"
        "/upcoming — показать уроки на ближайшие 24 часа\n"
        "/check — проверить изменения в расписании прямо сейчас\n"
        "/myid — узнать свой Chat ID для настройки уведомлений"
        f"{mode_note}"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=["myid"])
def handle_myid(message: telebot.types.Message) -> None:
    """Reply with the user's Telegram Chat ID."""
    bot.reply_to(message, f"Твой Chat ID: {message.chat.id}")


@bot.message_handler(commands=["schedule"])
def handle_schedule(message: telebot.types.Message) -> None:
    """Fetch and reply with the full lesson schedule."""
    lessons = altegio_api.fetch_lessons_from_altegio()
    if lessons:
        logic.save_schedule(lessons)
    text = logic.format_schedule_text(lessons)
    bot.reply_to(message, text)


@bot.message_handler(commands=["upcoming"])
def handle_upcoming(message: telebot.types.Message) -> None:
    """Reply with lessons starting within the next 24 hours."""
    lessons = altegio_api.fetch_lessons_from_altegio()
    upcoming = logic.get_upcoming_lessons(lessons, hours_ahead=24)
    if not upcoming:
        bot.reply_to(message, "На ближайшие 24 часа уроков гитары нет.")
        return

    text = "⏰ Уроки на ближайшие 24 часа:\n\n" + logic.format_schedule_text(upcoming)
    bot.reply_to(message, text)


@bot.message_handler(commands=["check"])
def handle_check(message: telebot.types.Message) -> None:
    """Manually trigger a schedule change check."""
    report = build_changes_report()
    if report is None:
        bot.reply_to(message, "Изменений в расписании не обнаружено. Все актуально!")
    else:
        bot.reply_to(message, report)


@bot.message_handler(content_types=["text"])
def handle_unknown_text(message: telebot.types.Message) -> None:
    """Handle unrecognized text messages gracefully."""
    bot.reply_to(
        message,
        "Я понимаю только команды расписания. Напиши /help, чтобы увидеть список команд.",
    )


def auto_monitor(interval_seconds: int = 300) -> None:
    """Periodically check Altegio for schedule updates and notify the admin."""
    while True:
        try:
            admin_id = config.ADMIN_CHAT_ID
            if admin_id and admin_id != "123456789" and not admin_id.startswith("your_"):
                report = build_changes_report()
                if report is not None:
                    bot.send_message(admin_id, report)
        except Exception as error:
            print(f"Background monitor error: {error}")

        time.sleep(interval_seconds)


def main() -> None:
    """Validate configuration and start the Telegram bot."""
    token = config.TELEGRAM_BOT_TOKEN
    if not token or token.startswith("тут_") or token.startswith("your_"):
        print("Error: Please set a valid TELEGRAM_BOT_TOKEN in your .env file.")
        return

    monitor_thread = threading.Thread(target=auto_monitor, daemon=True)
    monitor_thread.start()

    print("Bot is running. Press Ctrl+C to stop.")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)


if __name__ == "__main__":
    main()