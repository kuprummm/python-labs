from datetime import datetime

from streamstats import filter


def test_level_and_source() -> None:
    """Проверка фильтра по уровню и источнику."""
    events: list[dict[str, object]] = [
        {"level": "INFO", "source": "site"},
        {"level": "ERROR", "source": "site"},
        {"level": "ERROR", "source": "db"},
    ]

    result = list(filter.filter_line(iter(events), level="ERROR", source="db"))

    assert result == [events[2]]


def test_time() -> None:
    """Проверка периода, включая границы и разные пояса."""
    events: list[dict[str, object]] = [
        {"timestamp": "2026-10-23T12:00:00+03:00"},
        {"timestamp": "2026-10-23T12:01:00+03:00"},
        {"timestamp": "2026-10-23T09:02:00+00:00"},
        {"timestamp": "2026-10-23T12:03:00+03:00"},
    ]
    start_time = datetime.fromisoformat("2026-10-23T09:01:00Z")
    end_time = datetime.fromisoformat("2026-10-23T09:02:00Z")

    result = list(filter.filter_line(iter(events), start_time=start_time, end_time=end_time))

    assert result == [events[1], events[2]]


def test_without_filters() -> None:
    """Без фильтров события остаются на месте."""
    events: list[dict[str, object]] = [{"level": "INFO", "source": "site"}]

    assert list(filter.filter_line(iter(events))) == events
