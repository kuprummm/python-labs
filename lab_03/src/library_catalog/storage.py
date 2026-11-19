import json
from collections.abc import Iterable

from . import constants
from .errors import CorruptedFileError, InvalidBookValueError, UnknownFormarError
from .models import Book


def write_books(path: str, books: Iterable[Book]) -> None:
    """Сохранение каталога."""

    catalog_save: dict[str, object] = {"format_version": constants.FORMAT_VERSION}

    book_list: list[dict[str, object]] = []

    for book in books:
        book_dict: dict[str, object] = {
            "id": book.id,
            "title": book.title,
            "category": book.category,
            "year": book.year,
            "author": book.author,
            "pages": book.pages,
        }
        book_list.append(book_dict)

    catalog_save["books"] = book_list

    with open(path, "w", encoding="utf-8") as file:
        json.dump(catalog_save, file, ensure_ascii=False, indent=4)


def read_books(path: str) -> tuple[Book, ...]:
    """Загрузка каталога из файла."""
    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise CorruptedFileError("Некорректный JSON.")

        if not isinstance(data, dict):
            raise CorruptedFileError("Данные книги в файде поврежденны.")

        if "format_version" not in data or type(data["format_version"]) is not int:
            raise CorruptedFileError("Отсутствует версия формата.")

        if data["format_version"] not in constants.ALLOWED_VERISONS:
            raise UnknownFormarError("Не поддерживаемый формат файла.")

        if "books" not in data or not isinstance(data["books"], list):
            raise CorruptedFileError("Книга долэна быть в файле списком.")

        books = data["books"]
        loaded_books: list[Book] = []
        uses_id: list[str] = []

        for book in books:
            if not isinstance(book, dict):
                raise CorruptedFileError("Запись книги должна быть словарем.")

            if data["format_version"] == 1:
                if "genre" not in book:
                    raise CorruptedFileError("В старой записи книги нет поля genre.")

                book["category"] = book.pop("genre")

            for needed_fields in constants.BOOK_FIELDS:
                if needed_fields not in book:
                    raise CorruptedFileError(
                        f"Отсутствует обязательное поле {needed_fields}."
                    )
            try:
                load_book = Book(
                    id=book["id"],
                    title=book["title"],
                    category=book["category"],
                    year=book["year"],
                    author=book["author"],
                    pages=book["pages"],
                )
            except InvalidBookValueError:
                raise CorruptedFileError("Некорректная книга в файле")

            if book["id"] in uses_id:
                raise CorruptedFileError("Повторяющиеся айди книги.")

            uses_id.append(book["id"])
            loaded_books.append(load_book)

        return tuple(loaded_books)
