import json
import csv
import logging
from collections.abc import Iterator

from . import errors, validate


def pars_jsonl(path: str, stats: dict[str, int], skip_invalid: bool = False) -> Iterator[dict[str, object]]:
    """Парсер jsonl"""
    line_number = 0

    with open(path, encoding='utf-8') as file:
        for line in file:
            line_number += 1
            try:
                data = json.loads(line)

                if not isinstance(data, dict):
                    raise errors.InvalidEventValueError("Должна быть jsonl запись")

                validate.validate_event_line(data)

            except (json.JSONDecodeError, errors.StreamStatsError) as error:
                if not skip_invalid:
                    raise errors.InvalidParsEvent(f"в файле  '{path}' в строке {line_number} ощибка {error}")
                else:
                    logging.warning(f"Файл '{path}', строка {line_number}: {error}")
                    stats["skipped"] += 1
                    continue

            yield data


def pars_csv(path: str, stats: dict[str, int], skip_invalid: bool = False) -> Iterator[dict[str, object]]:
    """Парсер csv."""
    line_number = 1

    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for data in reader:
            line_number += 1

            try:
                validate.validate_event_line(data)

            except errors.StreamStatsError as error:
                if not skip_invalid:
                    raise errors.InvalidParsEvent(f"в файле  '{path}' в строке {line_number} ощибка {error}")
                else:
                    logging.warning(f"Файл '{path}', строка {line_number}: {error}")
                    stats["skipped"] += 1
                    continue

            yield data


def pars_custom_format(path: str, stats: dict[str, int], skip_invalid: bool = False) -> Iterator[dict[str, object]]:
    """Парсер пользовательского формата."""
    line_number = 0

    with open(path, encoding="utf-8") as file:
        for line in file:
            line_number += 1

            try:
                lst_line = line.replace('\n', '').split("|")

                if len(lst_line) != 4:
                    raise errors.InvalidEventValueError("В записи должно быть 4 поля")

                timestamp, level, source, message = lst_line

                data: dict[str, object] = {
                    "timestamp": timestamp,
                    "level": level,
                    "source": source,
                    "message": message,
                }

                validate.validate_event_line(data)

            except errors.StreamStatsError as error:
                if not skip_invalid:
                    raise errors.InvalidParsEvent(f"в файле  '{path}' в строке {line_number} ошибка - {error}")
                else:
                    logging.warning(f"Файл '{path}', строка {line_number}: {error}")
                    stats["skipped"] += 1
                    continue

            yield data


PARSERS = {
    "csv": pars_csv,
    "jsonl": pars_jsonl,
    "txt": pars_custom_format,
}

if __name__ == "__main__":
    # for i in pars_jsonl(r"C:\Users\kuprum\Desktop\python-labs2\lab_02\example\events.jsonl"):
    #     print(i)
    # for i in pars_csv(r"C:\Users\kuprum\Desktop\python-labs2\lab_02\example\events.csv"):
    #     print(i)
    stats = {"skipped": 0}
    for i in pars_custom_format(r"C:\Users\kuprum\Desktop\python-labs2\lab_02\example\events.txt", stats):
        print(i)
