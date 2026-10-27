import json
from datetime import datetime


def save_json_report(data: dict[str, object], path: str) -> None:
    """Сохранение отчета в json."""

    report = data.copy()

    first_time = report["first_time"]
    last_time = report["last_time"]

    if isinstance(first_time, datetime):
        report["first_time"] = first_time.isoformat()

    if isinstance(last_time, datetime):
        report["last_time"] = last_time.isoformat()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)
