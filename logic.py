import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Строим надежный путь к файлу кэша рядом с нашим модулем (Лекция 13 — pathlib)
CACHE_FILE: Path = Path(__file__).parent / "schedule_cache.json"


def load_saved_schedule(path: Path = CACHE_FILE) -> list[dict[str, Any]]:
    """
    Читает сохраненное ранее расписание из JSON-файла.
    Если файла еще нет или он поврежден — возвращает пустой список.
    """
    # Проверяем, существует ли файл (Лекция 13)
    if not path.exists():
        return []

    # Открываем файл через контекстный менеджер with с кодировкой utf-8 (Лекция 2, 7, 13)
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        # Если в файле битый JSON (Лекция 13) или ошибка чтения (Лекция 7), не падаем
        return []


def save_schedule(lessons: list[dict[str, Any]], path: Path = CACHE_FILE) -> None:
    """
    Сохраняет текущее расписание в JSON-файл (Лекция 13).
    """
    with path.open("w", encoding="utf-8") as file:
        # ensure_ascii=False сохраняет кириллицу читаемой, indent=2 делает красивые отступы
        json.dump(lessons, file, ensure_ascii=False, indent=2)


def find_schedule_changes(
    old_lessons: list[dict[str, Any]],
    new_lessons: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Сравнивает старый и новый списки уроков.
    Возвращает словарь с добавленными (added), отмененными (cancelled)
    и перенесенными (rescheduled) занятиями.
    """
    # Собираем словари {id_урока: словарь_урока} через Dict Comprehension (Лекция 3)
    old_by_id = {lesson["id"]: lesson for lesson in old_lessons}
    new_by_id = {lesson["id"]: lesson for lesson in new_lessons}

    added: list[dict[str, Any]] = []
    cancelled: list[dict[str, Any]] = []
    rescheduled: list[dict[str, Any]] = []

    # Ищем новые и перенесенные уроки (оператор in из Лекции 1 и 3)
    for lesson_id, new_lesson in new_by_id.items():
        if lesson_id not in old_by_id:
            added.append(new_lesson)
        elif old_by_id[lesson_id]["date"] != new_lesson["date"]:
            rescheduled.append(new_lesson)

    # Ищем отмененные уроки (были в старом расписании, но исчезли из нового)
    for lesson_id, old_lesson in old_by_id.items():
        if lesson_id not in new_by_id:
            cancelled.append(old_lesson)

    return {
        "added": added,
        "cancelled": cancelled,
        "rescheduled": rescheduled,
    }


def get_upcoming_lessons(
    lessons: list[dict[str, Any]],
    now: datetime | None = None,
    hours_ahead: int = 24,
) -> list[dict[str, Any]]:
    """
    Отбирает уроки, которые начнутся в ближайшие hours_ahead часов (Лекция 13).
    """
    # Как учили в Лекции 5, для дефолтного значения используем None
    if now is None:
        now = datetime.now()

    limit_time = now + timedelta(hours=hours_ahead)
    upcoming: list[dict[str, Any]] = []

    for lesson in lessons:
        try:
            # Переводим строку ISO обратно в объект datetime (Лекция 13)
            lesson_time = datetime.fromisoformat(lesson["date"])
        except (ValueError, KeyError):
            continue  # Пропускаем запись, если дата некорректна (Лекция 2 — continue)

        # Цепочка сравнений как в математике (Лекция 1)
        if now <= lesson_time <= limit_time:
            upcoming.append(lesson)

    return upcoming


def format_schedule_text(lessons: list[dict[str, Any]]) -> str:
    """
    Форматирует список уроков в красивое текстовое сообщение для Telegram.
    """
    if not lessons:
        return "В расписании пока нет записей на уроки гитары."

    lines: list[str] = ["🎸 Расписание уроков игры на гитаре:"]

    # Нумеруем уроки с единицы с помощью функции enumerate (Лекция 2 и 9)
    for index, lesson in enumerate(lessons, start=1):
        raw_date = lesson.get("date", "")
        try:
            # Делаем дату красивой и понятной человеку: ДД.ММ.ГГГГ ЧЧ:ММ (Лекция 13)
            dt = datetime.fromisoformat(raw_date)
            readable_date = dt.strftime("%d.%m.%Y в %H:%M")
        except ValueError:
            readable_date = raw_date

        client = lesson.get("client_name", "Ученик")
        service = lesson.get("service", "Урок гитары")
        
        lines.append(f"{index}. {readable_date} — {client} ({service})")

    # Склеиваем список строк через символ переноса строки \n (Лекция 1 — метод .join)
    return "\n".join(lines)