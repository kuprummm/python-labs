from collections.abc import Iterator
from datetime import datetime
from typing import cast


def filter_line(events: Iterator[dict[str, object]], level: str | None = None, source: str | None = None, start_time: datetime | None = None, end_time: datetime | None = None,) -> Iterator[dict[str, object]]:
    """Фильтрация событий."""

    for event in events:
        if (level is not None) and (event["level"] != level):
            continue
        if (source is not None) and (event["source"] != source):
            continue
        if (start_time is not None) and (start_time > datetime.fromisoformat(cast(str, event["timestamp"]))):
            continue
        if (end_time is not None) and (end_time < datetime.fromisoformat(cast(str, event["timestamp"]))):
            continue

        yield event
