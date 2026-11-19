from pathlib import Path

import pytest

from library_catalog.catalog import Catalog
from library_catalog.errors import (
    BookNotFoundedError,
    CorruptedFileError,
    DoubleIDError,
    HistoryError,
)
from library_catalog.models import Book


def test_undo_empty() -> None:
    """В пустой истории нечего отменять."""
    catalog = Catalog()

    with pytest.raises(HistoryError):
        catalog.undo()


def test_undo_add(books: list[Book]) -> None:
    """Отменяем добавление книги."""
    catalog = Catalog()
    catalog.add(books[0])

    catalog.undo()

    assert len(catalog) == 0
    assert "001" not in catalog
    assert catalog.find_by_category("Фантастика") == ()
    assert "фантастика" not in catalog._category


def test_undo_remove(books: list[Book]) -> None:
    """Удалённая книга возвращается в свой жанр."""
    catalog = Catalog()
    catalog.add(books[0])
    catalog.add(books[1])
    catalog.remove("001")

    catalog.undo()

    assert catalog.get("001") == books[0]
    assert catalog.get("002") == books[1]
    assert catalog._category["фантастика"] == {"001", "002"}
    assert len(catalog) == 2


def test_undo_many(books: list[Book]) -> None:
    """Несколько действий отменяются с конца."""
    catalog = Catalog()
    catalog.add(books[0])
    catalog.add(books[1])
    catalog.remove("001")

    catalog.undo()
    assert list(catalog) == [books[0], books[1]]

    catalog.undo()
    assert list(catalog) == [books[0]]

    catalog.undo()
    assert len(catalog) == 0
    assert catalog.find_by_category("Фантастика") == ()

    with pytest.raises(HistoryError):
        catalog.undo()


def test_undo_error(books: list[Book]) -> None:
    """Действия с ошибкой в историю не попадают."""
    catalog = Catalog()
    catalog.add(books[0])

    with pytest.raises(DoubleIDError):
        catalog.add(books[0])

    with pytest.raises(BookNotFoundedError):
        catalog.remove("missing")

    catalog.undo()
    assert len(catalog) == 0

    with pytest.raises(HistoryError):
        catalog.undo()


def test_load_history(examples: Path, books: list[Book]) -> None:
    """После загрузки другого файла старая история очищается."""
    catalog = Catalog()
    catalog.add(books[0])

    catalog.load(str(examples / "one_book.json"))

    with pytest.raises(HistoryError):
        catalog.undo()

    assert list(catalog) == [books[2]]


def test_bad_load_history(examples: Path, books: list[Book]) -> None:
    """При ошибке загрузки прежняя история остаётся."""
    catalog = Catalog()
    catalog.add(books[0])

    with pytest.raises(CorruptedFileError):
        catalog.load(str(examples / "bad_second.json"))

    catalog.undo()

    assert len(catalog) == 0
    assert catalog.find_by_category("Фантастика") == ()
