import json
from pathlib import Path

import pytest

from library_catalog.catalog import Catalog
from library_catalog.errors import CorruptedFileError
from library_catalog.models import Book
from library_catalog.storage import read_books


def test_read_old(examples: Path, books: list[Book]) -> None:
    """Старый файл с полем genre читается как обычный."""
    result = read_books(str(examples / "books_v1.json"))

    assert result == tuple(books)


def test_save_new(examples: Path, tmp_path: Path, books: list[Book]) -> None:
    """Читаем версию 1, а сохраняем версию 2 с полем category."""
    source = examples / "books_v1.json"
    old_text = source.read_text(encoding="utf-8")
    path = tmp_path / "saved.json"
    catalog = Catalog()

    catalog.load(str(source))
    catalog.save(str(path))

    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    assert data["format_version"] == 2
    for book in data["books"]:
        assert "category" in book
        assert "genre" not in book
    assert read_books(str(path)) == tuple(books)
    assert catalog._category["фантастика"] == {"001", "002"}
    assert source.read_text(encoding="utf-8") == old_text


def test_no_genre(examples: Path) -> None:
    """В старой записи обязательно поле genre."""
    with pytest.raises(CorruptedFileError):
        read_books(str(examples / "v1_no_genre.json"))


def test_bad_old(examples: Path, books: list[Book]) -> None:
    """Ошибка в старом файле тоже оставляет прежние книги на месте."""
    catalog = Catalog()
    catalog.add(books[0])

    with pytest.raises(CorruptedFileError):
        catalog.load(str(examples / "v1_bad_second.json"))

    assert list(catalog) == [books[0]]
    assert catalog.find_by_category("Фантастика") == (books[0],)
    assert catalog.find_by_category("Роман") == ()
