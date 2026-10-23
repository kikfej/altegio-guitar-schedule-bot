import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Path to the local JSON schedule cache located next to this module
CACHE_FILE: Path = Path(__file__).parent / "schedule_cache.json"


def load_saved_schedule(path: Path = CACHE_FILE) -> list[dict[str, Any]]:
    """Load cached lessons from a JSON file. Returns an empty list if missing or invalid."""
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    # Ensure the loaded JSON is actually a list of dictionaries
    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def save_schedule(lessons: list[dict[str, Any]], path: Path = CACHE_FILE) -> None:
    """Save the current list of lessons to a JSON file."""
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(lessons, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Failed to save schedule cache: {error}")


def find_schedule_changes(
    old_lessons: list[dict[str, Any]],
    new_lessons: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Compare previous and current lesson lists by lesson ID.
    Returns a dictionary with 'added', 'cancelled', and 'rescheduled' lessons.
    """
    old_by_id = {
        lesson["id"]: lesson
        for lesson in old_lessons
        if "id" in lesson and "date" in lesson
    }
    new_by_id = {
        lesson["id"]: lesson
        for lesson in new_lessons
        if "id" in lesson and "date" in lesson
    }

    added: list[dict[str, Any]] = []
    cancelled: list[dict[str, Any]] = []
    rescheduled: list[dict[str, Any]] = []

    for lesson_id, new_lesson in new_by_id.items():
        if lesson_id not in old_by_id:
            added.append(new_lesson)
        elif old_by_id[lesson_id].get("date") != new_lesson.get("date"):
            rescheduled.append(new_lesson)

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
    """Filter lessons that start within the next `hours_ahead` hours."""
    if now is None:
        now = datetime.now()

    limit_time = now + timedelta(hours=hours_ahead)
    upcoming: list[dict[str, Any]] = []

    for lesson in lessons:
        raw_date = str(lesson.get("date", ""))
        try:
            lesson_time = datetime.fromisoformat(raw_date)
        except ValueError:
            continue

        # Convert timezone-aware datetime to naive local format if needed to avoid TypeError
        if lesson_time.tzinfo is not None and now.tzinfo is None:
            lesson_time = lesson_time.replace(tzinfo=None)

        if now <= lesson_time <= limit_time:
            upcoming.append(lesson)

    return upcoming


def format_schedule_text(lessons: list[dict[str, Any]]) -> str:
    """Format a list of lesson dictionaries into a human-readable Telegram message."""
    if not lessons:
        return "В расписании пока нет записей на уроки гитары."

    lines: list[str] = ["🎸 Расписание уроков игры на гитаре:"]

    for index, lesson in enumerate(lessons, start=1):
        raw_date = str(lesson.get("date", ""))
        try:
            dt = datetime.fromisoformat(raw_date)
            readable_date = dt.strftime("%d.%m.%Y в %H:%M")
        except ValueError:
            readable_date = raw_date

        client = lesson.get("client_name", "Ученик")
        service = lesson.get("service", "Урок гитары")
        lines.append(f"{index}. {readable_date} — {client} ({service})")

    return "\n".join(lines)