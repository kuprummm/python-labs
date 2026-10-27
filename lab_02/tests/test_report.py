import json
from datetime import datetime
from pathlib import Path

from streamstats import report


def test_save_report(tmp_path: Path) -> None:
    """Проверка записи JSON и преобразования даты в строку."""
    date = datetime.fromisoformat("2026-10-23T12:00:00Z")
    data: dict[str, object] = {"total": 1, "first_time": date, "last_time": date, "skipped": 0}
    path = tmp_path / "report.json"

    report.save_json_report(data, str(path))
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["total"] == 1
    assert result["first_time"] == "2026-10-23T12:00:00+00:00"
    assert data["first_time"] == date


def test_empty_report(tmp_path: Path) -> None:
    """Пустые даты записываются как null."""
    data: dict[str, object] = {"total": 0, "first_time": None, "last_time": None}
    path = tmp_path / "report.json"

    report.save_json_report(data, str(path))
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["first_time"] is None
    assert result["last_time"] is None
