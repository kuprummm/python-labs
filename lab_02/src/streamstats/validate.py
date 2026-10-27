from datetime import datetime, timezone

from . import constants, errors


def validate_event_line(data: dict[str, object]) -> None:
    """Проверка корректности данных стоки."""

    data_keys = list(data.keys())

    for allowed_event_keys in constants.ALLOWED_KEYS:
        if allowed_event_keys not in data_keys:
            raise errors.MissingFieldError("Отсутствует одно из ключевых полей.")

    event_date = data["timestamp"]
    event_level = data["level"]
    event_source = data["source"]

    for event_keys in constants.ALLOWED_KEYS:
        if not isinstance(data[event_keys], str):
            raise errors.InvalidEventValueError(f"Формат поля {event_keys} не строка.")

    if event_level not in constants.ALLOWED_LEVELS:
        raise errors.InvalidEventValueError("Недопустимый уровень.")

    if not isinstance(event_date, str):
        raise errors.InvalidEventValueError("Поле 'timestamp' должно быть строкой.")

    if not isinstance(event_source, str):
        raise errors.InvalidEventValueError("Поле 'source' должно быть строкой.")

    try:
        event_date = datetime.fromisoformat(event_date)
    except ValueError:
        raise errors.InvalidTimeFormatError("Некоректный формат времени.")

    if not event_source.strip():
        raise errors.InvalidEventValueError("Строка источника не должна быть пустой.")

    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)

    data["timestamp"] = event_date.isoformat()


if __name__ == "__main__":
    validate_event_line({
            "timestamp":"2026-10-14T10:03:01+00:00",
            "level":"CRITICAL",
            "source":"database",
            "message":"База недоступна"
        })
