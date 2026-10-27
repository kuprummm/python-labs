import argparse
import sys
import tracemalloc
from collections.abc import Iterator
from datetime import datetime, timezone

from . import analysis, filter, parsers, report, errors


def read_line_events(paths: list[str], anylis_format: str, stats: dict[str, int], skip_invalid: bool) -> Iterator[dict[str, object]]:
    """Сбор событий со всех файлов."""

    parser_function = parsers.PARSERS[anylis_format]

    for file in paths:
        for event in parser_function(file, stats=stats, skip_invalid=skip_invalid):
            yield event


def main() -> int:
    """Разбор аргументов и запуск."""

    tracemalloc.start()

    parser = argparse.ArgumentParser(description="Анализ логов")

    commands = parser.add_subparsers(dest="command", required=True)

    anylis_parser = commands.add_parser("analyze")

    anylis_parser.add_argument("inputs", nargs="+")
    anylis_parser.add_argument("--format", choices=list(parsers.PARSERS), required=True)
    anylis_parser.add_argument("--output", default="report.json")
    anylis_parser.add_argument("--skip-invalid", action="store_true")

    anylis_parser.add_argument("--level")
    anylis_parser.add_argument("--source")
    anylis_parser.add_argument("--start-time")
    anylis_parser.add_argument("--last-time")

    args = parser.parse_args()

    stats = {"skipped": 0}

    start_time: datetime | None = None
    last_time: datetime | None = None

    try:
        if args.start_time is not None:
            start_time = datetime.fromisoformat(args.start_time)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)

        if args.last_time is not None:
            last_time = datetime.fromisoformat(args.last_time)
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)
    except ValueError:
        parser.error("Неправильный формат времени.")
    if last_time is not None and start_time is not None:
        if start_time > last_time:
            parser.error("Начальная дата позже конечной.")

    try:
        events = read_line_events(paths=args.inputs, anylis_format=args.format, stats=stats, skip_invalid=args.skip_invalid)

        filtered_events = filter.filter_line(events, level=args.level, source=args.source, start_time=start_time, end_time=last_time)

        result = analysis.analys(filtered_events)
        result["skipped"] = stats["skipped"]

        report.save_json_report(result, args.output)
    except (errors.StreamStatsError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Использовали: {peak} байт")

    return 0
