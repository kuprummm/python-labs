from datetime import datetime

from streamstats import analysis


def event(level: str, source: str, minute: int = 0) -> dict[str, object]:
    """Создать событие для проверки."""
    return {
        "timestamp": f"2026-10-23T12:{minute:02}:00+03:00",
        "level": level, "source": source, "message": "Тест",
    }


def test_counts() -> None:
    """Проверка количества событий по уровням и источникам."""
    events = [event("INFO", "site"), event("ERROR", "site"), event("CRITICAL", "site")]
    result = analysis.analys(iter(events))

    assert result["total"] == 3
    assert result["by_source"] == {"site": 3}
    assert result["by_level"] == {
        "DEBUG": 0, "INFO": 1, "WARNING": 0, "ERROR": 1, "CRITICAL": 1,
    }
    assert result["top_error_sources"] == [{"source": "site", "count": 2}]


def test_first_and_last_time() -> None:
    """Проверка самой ранней и поздней даты."""
    events = [event("INFO", "site", 2), event("INFO", "site", 1), event("INFO", "site", 3)]
    result = analysis.analys(iter(events))

    assert result["first_time"] == datetime.fromisoformat("2026-10-23T12:01:00+03:00")
    assert result["last_time"] == datetime.fromisoformat("2026-10-23T12:03:00+03:00")


def test_empty_events() -> None:
    """Проверка пустого потока."""
    result = analysis.analys(iter([]))

    assert result["total"] == 0
    assert result["by_source"] == {}
    assert result["top_error_sources"] == []
    assert result["first_time"] is None
    assert result["last_time"] is None
