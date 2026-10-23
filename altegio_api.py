from datetime import datetime, timedelta
from typing import Any
import requests

import config


def get_demo_lessons() -> list[dict[str, Any]]:
    """Generate sample guitar lessons relative to the current time for demo mode."""
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    return [
        {
            "id": 101,
            "client_name": "Алексей Смирнов",
            "service": "Электрогитара (индивидуальный урок)",
            "date": (now + timedelta(hours=2)).isoformat(),
        },
        {
            "id": 102,
            "client_name": "Мария Иванова",
            "service": "Акустическая гитара (разбор песен)",
            "date": (now + timedelta(days=1, hours=3)).isoformat(),
        },
    ]


def fetch_lessons_from_altegio() -> list[dict[str, Any]]:
    """
    Fetch lesson records from the Altegio REST API.
    Returns an empty list on any network or data format error.
    """
    if config.USE_DEMO_MODE:
        return get_demo_lessons()

    url = f"https://api.alteg.io/api/v1/records/{config.ALTEGIO_COMPANY_ID}"
    headers = {
        "Accept": "application/vnd.api.v2+json",
        "Authorization": f"Bearer {config.ALTEGIO_PARTNER_TOKEN}, User {config.ALTEGIO_USER_TOKEN}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Altegio API error: {error}")
        return []

    # Guard against unexpected JSON root types (e.g., list instead of dict)
    if not isinstance(raw_data, dict):
        return []

    records = raw_data.get("data", [])
    if not isinstance(records, list):
        return []

    lessons: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(record, dict):
            continue

        client = record.get("client")
        if not isinstance(client, dict):
            client = {}

        services = record.get("services")
        if not isinstance(services, list):
            services = []

        first_service = services[0] if services and isinstance(services[0], dict) else {}
        service_title = first_service.get("title", "Урок гитары")
        raw_date = str(record.get("date", "")).replace(" ", "T")

        try:
            record_id = int(record.get("id", 0))
        except (ValueError, TypeError):
            continue

        lessons.append({
            "id": record_id,
            "client_name": str(client.get("name", "Неизвестный ученик")),
            "service": str(service_title),
            "date": raw_date,
        })

    return lessons