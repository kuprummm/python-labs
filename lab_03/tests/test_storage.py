import json
from pathlib import Path

import pytest

from library_catalog import constants
from library_catalog.catalog import Catalog
from library_catalog.errors import CorruptedFileError, UnknownFormarError
from library_catalog.models import Book
from library_catalog.storage import read_books, write_books


def test_write(tmp_path: Path, books: list[Book]) -> None:
    """Записываем книги и читаем обратно."""
    path = tmp_path / "saved.json"

    write_books(str(path), books)

    assert read_books(str(path)) == tuple(books)
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    assert data["format_version"] == constants.FORMAT_VERSION
    assert len(data["books"]) == 3
    assert data["books"][0]["title"] == "Дюна"


def test_empty(examples: Path) -> None:
    """В файле нет книг."""
    assert read_books(str(examples / "empty.json")) == ()


def test_bad_json(examples: Path) -> None:
    """JSON сломан."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "bad_json.json"))


def test_bad_root(examples: Path) -> None:
    """В начале файла должен быть словарь."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "bad_root.json"))


def test_no_version(examples: Path) -> None:
    """Нет номера версии."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "no_version.json"))


def test_bad_version(examples: Path) -> None:
    """Версия неизвестна."""
    with pytest.raises(UnknownFormarError):
        read_books(str(examples / "bad_version.json"))


def test_bad_list(examples: Path) -> None:
    """В books должен быть список."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "bad_list.json"))


def test_bad_book(examples: Path) -> None:
    """Вместо книги записана строка."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "bad_book.json"))


def test_no_author(examples: Path) -> None:
    """В записи нет поля author."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "no_author.json"))


def test_same_id(examples: Path) -> None:
    """У двух книг одинаковый ID."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "same_id.json"))


def test_save(tmp_path: Path, books: list[Book]) -> None:
    """Сохраняем каталог его методом save."""
    path = tmp_path / "saved.json"
    catalog = Catalog()
    catalog.add(books[0])

    catalog.save(str(path))

    assert read_books(str(path)) == (books[0],)


def test_load(examples: Path, books: list[Book]) -> None:
    """При загрузке новые книги заменяют старые."""
    catalog = Catalog()
    catalog.add(books[0])

    catalog.load(str(examples / "one_book.json"))

    assert tuple(catalog) == (books[2],)
    assert "001" not in catalog
    assert catalog.find_by_category("Фантастика") == ()
    assert catalog.find_by_category("Роман") == (books[2],)


def test_bad_load(examples: Path, books: list[Book]) -> None:
    """Вторая книга с ошибкой. Старые книги остаются на месте."""
    catalog = Catalog()
    catalog.add(books[0])

    with pytest.raises(CorruptedFileError):
        catalog.load(str(examples / "bad_second.json"))

    assert tuple(catalog) == (books[0],)
    assert "004" not in catalog
    assert catalog.find_by_category("Фантастика") == (books[0],)
    assert catalog.find_by_category("Роман") == ()
