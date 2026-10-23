from datetime import datetime
from pathlib import Path

import logic


def test_save_and_load_schedule(tmp_path: Path) -> None:
    """Verify saving and loading schedule data using a temporary file."""
    temp_file = tmp_path / "test_cache.json"
    sample_lessons = [
        {
            "id": 1,
            "client_name": "Иван",
            "service": "Бас-гитара",
            "date": "2026-10-20T15:00:00",
        }
    ]

    logic.save_schedule(sample_lessons, path=temp_file)
    loaded = logic.load_saved_schedule(path=temp_file)

    assert loaded == sample_lessons


def test_find_schedule_changes() -> None:
    """Verify detection of added, cancelled, and rescheduled lessons."""
    old_lessons = [
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T10:00:00"},
        {"id": 2, "client_name": "Петр", "service": "Гитара", "date": "2026-10-20T12:00:00"},
    ]
    new_lessons = [
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T11:00:00"},
        {"id": 3, "client_name": "Олег", "service": "Укулеле", "date": "2026-10-21T14:00:00"},
    ]

    changes = logic.find_schedule_changes(old_lessons, new_lessons)

    assert len(changes["added"]) == 1
    assert changes["added"][0]["id"] == 3

    assert len(changes["cancelled"]) == 1
    assert changes["cancelled"][0]["id"] == 2

    assert len(changes["rescheduled"]) == 1
    assert changes["rescheduled"][0]["id"] == 1


def test_get_upcoming_lessons() -> None:
    """Verify filtering of lessons within the next 24 hours."""
    fixed_now = datetime(2026, 10, 20, 12, 0)
    lessons = [
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T15:00:00"},
        {"id": 2, "client_name": "Петр", "service": "Гитара", "date": "2026-10-23T15:00:00"},
    ]

    upcoming = logic.get_upcoming_lessons(lessons, now=fixed_now, hours_ahead=24)

    assert len(upcoming) == 1
    assert upcoming[0]["id"] == 1


def test_format_empty_schedule() -> None:
    """Verify formatting behavior when the lesson list is empty."""
    result = logic.format_schedule_text([])
    assert "нет записей" in result