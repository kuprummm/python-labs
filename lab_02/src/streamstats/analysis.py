from datetime import datetime
from collections.abc import Iterator
from typing import cast
from . import constants, parsers, filter


def creste_top_error(source_error_count: dict[str, int]) -> list[dict[str, object]]:
    """Создание топа ошибок"""

    sorted_errors = sorted(source_error_count.items(), key=lambda x:(-x[1], x[0]))

    top_errors_dict = dict(sorted_errors[:min(len(sorted_errors), constants.POSITION_TOP)])
    result = []

    for line in list(top_errors_dict.keys()):
        result.append({"source": line, "count": top_errors_dict[line]})

    return result


def analys(events: Iterator[dict[str, object]]) -> dict[str, object]:
    """Считаем статистику переданных строк."""
    total = 0

    level_count: dict[str, int] = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
    source_count: dict[str, int] = {}
    source_error_count: dict[str, int] = {}

    first_time: datetime | None = None
    last_time: datetime | None = None

    for event in events:
        total += 1

        level_count[cast(str, event["level"])] += 1

        event_source = cast(str, event["source"])

        if event_source in source_count:
            source_count[event_source] += 1
        else:
            source_count[event_source] = 1

        if event["level"] in constants.CRYTICAL_LEVELS:
            if event_source in source_error_count:
                source_error_count[event_source] += 1
            else:
                source_error_count[event_source] = 1

        event_time = datetime.fromisoformat(cast(str, event["timestamp"]))

        if first_time is None or event_time < first_time:
            first_time = event_time

        if last_time is None or event_time > last_time:
            last_time = event_time

    top_error_sources = creste_top_error(source_error_count)

    return {
        "total": total,
        "by_level": level_count,
        "by_source": source_count,
        "top_error_sources": top_error_sources,
        "first_time": first_time,
        "last_time": last_time,
    }


if __name__ == "__main__":
    # print(creste_top_error({"database": 6, "website2": 1, "database2": 7, "website3": 1, "database3": 8, "website4": 11}))

    stats = {"skipped": 0}

    events = parsers.pars_csv(r"C:\Users\kuprum\Desktop\python-labs2\lab_02\example\events.csv", stats=stats)

    filtered_events = filter.filter_line(events, level="ERROR", source="website")

    # print(analys(events))
    print(analys(filtered_events))
    print("Пропущено:", stats["skipped"])
