from datetime import datetime
from pathlib import Path

import logic


def test_save_and_load_schedule(tmp_path: Path) -> None:
    """
    Тест 1: проверяем сохранение и загрузку JSON-файла.
    Используем фикстуру tmp_path из Лекции 14 для создания временного файла.
    """
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
    """
    Тест 2: проверяем поиск новых, отмененных и перенесенных уроков.
    """
    old_lessons = [
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T10:00:00"},
        {"id": 2, "client_name": "Петр", "service": "Гитара", "date": "2026-10-20T12:00:00"},
    ]
    new_lessons = [
        # Урок с id=1 перенесли с 10:00 на 11:00
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T11:00:00"},
        # Урок с id=2 отменили (его нет в новом списке), но добавили урок с id=3
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
    """
    Тест 3: проверяем фильтр уроков на ближайшие 24 часа.
    """
    fixed_now = datetime(2026, 10, 20, 12, 0)
    lessons = [
        # Через 3 часа (должен попасть в список)
        {"id": 1, "client_name": "Анна", "service": "Гитара", "date": "2026-10-20T15:00:00"},
        # Через 3 дня (не должен попасть в список на 24 часа)
        {"id": 2, "client_name": "Петр", "service": "Гитара", "date": "2026-10-23T15:00:00"},
    ]

    upcoming = logic.get_upcoming_lessons(lessons, now=fixed_now, hours_ahead=24)

    assert len(upcoming) == 1
    assert upcoming[0]["id"] == 1


def test_format_empty_schedule() -> None:
    """
    Тест 4: проверяем граничный случай — форматирование пустого списка уроков (Лекция 14).
    """
    result = logic.format_schedule_text([])
    assert "нет записей" in result