from datetime import datetime, timedelta
from typing import Any
import requests

import config


def get_demo_lessons() -> list[dict[str, Any]]:
    """
    Возвращает учебное расписание уроков гитары (для работы без ключей Altegio).
    Использует datetime и timedelta из Лекции 13.
    """
    # Берем текущее время без секунд и микросекунд
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    # Возвращаем список словарей (Лекция 1 и 3)
    return [
        {
            "id": 101,
            "client_name": "Алексей Смирнов",
            "service": "Электрогитара (индивидуальный урок)",
            "date": (now + timedelta(hours=2)).isoformat(),  # Урок через 2 часа
        },
        {
            "id": 102,
            "client_name": "Мария Иванова",
            "service": "Акустическая гитара (разбор песен)",
            "date": (now + timedelta(days=1, hours=3)).isoformat(),  # Урок завтра
        },
    ]


def fetch_lessons_from_altegio() -> list[dict[str, Any]]:
    """
    Загружает список записей на уроки из API Altegio.
    При ошибке сети возвращает пустой список, не роняя программу (Требование курса).
    """
    # 1. Если включен демо-режим, сразу отдаем тестовые уроки
    if config.USE_DEMO_MODE:
        return get_demo_lessons()

    # 2. Формируем URL-адрес запроса с помощью f-строки (Лекция 2)
    url = f"https://api.alteg.io/api/v1/records/{config.ALTEGIO_COMPANY_ID}"

    # 3. Заголовки запроса (наш "пропуск" по правилам документации Altegio)
    headers = {
        "Accept": "application/vnd.api.v2+json",
        "Authorization": f"Bearer {config.ALTEGIO_PARTNER_TOKEN}, User {config.ALTEGIO_USER_TOKEN}",
    }

    # 4. Делаем запрос внутри блока try...except (Лекция 7 — Исключения)
    try:
        # timeout=10 гарантирует, что бот не зависнет навсегда, если сервер не отвечает
        response = requests.get(url, headers=headers, timeout=10)
        
        # Если сервер вернул ошибку (например, 401 Неверный пароль или 404 Не найдено),
        # метод raise_for_status() выбросит исключение RequestException
        response.raise_for_status()
        
        # Переводим JSON-ответ сервера в обычный словарь Python (Лекция 13)
        raw_data = response.json()
        
    except requests.RequestException as error:
        # Перехватываем любую ошибку сети, печатаем в консоль и возвращаем пустой список
        print(f"Ошибка при запросе к Altegio API: {error}")
        return []

    # 5. Вытаскиваем список записей из ответа и упрощаем структуру
    records = raw_data.get("data", [])
    lessons: list[dict[str, Any]] = []

    # Перебираем записи циклом for (Лекция 2)
    for record in records:
        # Безопасно достаем вложенные словари через .get() (Лекция 3)
        client = record.get("client") or {}
        services = record.get("services") or []
        
        # Берем название первой услуги (например, "Урок гитары"), если она есть
        service_title = services[0].get("title", "Урок гитары") if services else "Урок гитары"
        
        # Дата в Altegio приходит в формате "2026-10-19 18:00:00",
        # заменяем пробел на "T" методом .replace() (Лекция 1) для стандарта ISO
        raw_date = str(record.get("date", "")).replace(" ", "T")

        lessons.append({
            "id": int(record.get("id", 0)),
            "client_name": client.get("name", "Неизвестный ученик"),
            "service": service_title,
            "date": raw_date,
        })

    return lessons