class StreamStatsError(ValueError):
    """Базовая ошибка."""


class MissingFieldError(StreamStatsError):
    """Отсутствующее обязательное поле."""


class InvalidEventValueError(StreamStatsError):
    """Неправильный тип или значение поля."""


class InvalidTimeFormatError(InvalidEventValueError):
    """Неверная временная метка."""


class UnsupportedFileFormatError(StreamStatsError):
    """Неподдерживаемый формат файла."""


class CLIConfigurationError(StreamStatsError):
    """Ошибка конфигурации CLI."""


class InvalidParsEvent(StreamStatsError):
    """Ошибка парсинга"""
