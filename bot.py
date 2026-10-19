import threading
import time
import telebot

import config
import altegio_api
import logic

# Создаем объект бота и передаем ему токен из модуля config (Требование курса)
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


def build_changes_report() -> str | None:
    """
    Вспомогательная функция: скачивает свежее расписание из Altegio,
    сравнивает с сохраненным в JSON и возвращает текст отчета об изменениях.
    Если изменений нет — возвращает None (Лекция 1 и 4).
    """
    new_lessons = altegio_api.fetch_lessons_from_altegio()
    if not new_lessons:
        return None

    old_lessons = logic.load_saved_schedule()
    changes = logic.find_schedule_changes(old_lessons, new_lessons)

    # Сохраняем актуальное расписание в JSON-файл (Лекция 13)
    logic.save_schedule(new_lessons)

    # Если старого файла еще не было (первый запуск), уведомление не шлем
    if not old_lessons:
        return None

    added = changes["added"]
    cancelled = changes["cancelled"]
    rescheduled = changes["rescheduled"]

    # Если все три списка пусты, значит изменений не произошло (Лекция 1)
    if not added and not cancelled and not rescheduled:
        return None

    # Собираем текст уведомления с помощью списка и f-строк (Лекция 2)
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


# Декоратор из Лекции 11: привязывает функцию к командам /start и /help
@bot.message_handler(commands=["start", "help"])
def handle_start(message: telebot.types.Message) -> None:
    """Приветствует пользователя и выводит список доступных команд."""
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
    """Показывает пользователю его ID чата в Telegram."""
    bot.reply_to(message, f"Твой Chat ID: {message.chat.id}")


@bot.message_handler(commands=["schedule"])
def handle_schedule(message: telebot.types.Message) -> None:
    """Загружает и отправляет полное расписание уроков."""
    lessons = altegio_api.fetch_lessons_from_altegio()
    logic.save_schedule(lessons)
    text = logic.format_schedule_text(lessons)
    bot.reply_to(message, text)


@bot.message_handler(commands=["upcoming"])
def handle_upcoming(message: telebot.types.Message) -> None:
    """Показывает занятия на ближайшие 24 часа (напоминание)."""
    lessons = altegio_api.fetch_lessons_from_altegio()
    upcoming = logic.get_upcoming_lessons(lessons, hours_ahead=24)
    if not upcoming:
        bot.reply_to(message, "На ближайшие 24 часа уроков гитары нет.")
        return

    text = "⏰ Уроки на ближайшие 24 часа:\n\n" + logic.format_schedule_text(upcoming)
    bot.reply_to(message, text)


@bot.message_handler(commands=["check"])
def handle_check(message: telebot.types.Message) -> None:
    """Вручную проверяет, изменилось ли расписание с момента прошлой проверки."""
    report = build_changes_report()
    if report is None:
        bot.reply_to(message, "Изменений в расписании не обнаружено. Все актуально!")
    else:
        bot.reply_to(message, report)


# Обработчик любых других текстовых сообщений (Требование курса: не падать на вводе)
@bot.message_handler(content_types=["text"])
def handle_unknown_text(message: telebot.types.Message) -> None:
    """Вежливо отвечает на неизвестные команды и обычный текст."""
    bot.reply_to(
        message,
        "Я понимаю только команды расписания. Напиши /help, чтобы увидеть список команд.",
    )


def auto_monitor(interval_seconds: int = 300) -> None:
    """
    Фоновая функция (Шаг 5): каждые interval_seconds секунд проверяет
    расписание в Altegio и отправляет уведомление администратору в Telegram.
    """
    # Бесконечный цикл while (Лекция 2)
    while True:
        # Оборачиваем в try...except Exception (Лекция 7), чтобы фоновый поток не упал
        try:
            if config.ADMIN_CHAT_ID and config.ADMIN_CHAT_ID != "123456789":
                report = build_changes_report()
                if report is not None:
                    bot.send_message(config.ADMIN_CHAT_ID, report)
        except Exception as error:
            print(f"Ошибка в фоновом мониторинге: {error}")

        # Пауза перед следующей проверкой (time.sleep из Лекции 7)
        time.sleep(interval_seconds)


def main() -> None:
    """Точка входа в программу (Лекция 11)."""
    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "тут_будет_токен_телеграм":
        print("ОШИБКА: Укажи реальный TELEGRAM_BOT_TOKEN в файле .env!")
        return

    # Запускаем фоновую проверку расписания в отдельном потоке
    monitor_thread = threading.Thread(target=auto_monitor, daemon=True)
    monitor_thread.start()

    print("Бот успешно запущен! Для остановки нажми Ctrl+C в терминале.")
    bot.infinity_polling()


# Конструкция из Лекции 11: код запустится только при прямом запуске файла bot.py
if __name__ == "__main__":
    main()