class CatalogError(ValueError):
    """Общая ошибка программы"""


class InvalidBookValueError(CatalogError):
    """Ошибка данных книги"""


class DoubleIDError(CatalogError):
    """Повторный айди"""


class BookNotFoundedError(CatalogError):
    """Книга не найдена"""


class CategoryNotFoundedError(CatalogError):
    """Категория не найдена"""


class UnknownFormarError(CatalogError):
    """Неизвестный формат файла"""


class CorruptedFileError(CatalogError):
    """Поврежденный файл"""


class HistoryError(CatalogError):
    """Ошибка истории записей действий"""
