from dataclasses import FrozenInstanceError

import pytest

from library_catalog.catalog import Catalog
from library_catalog.models import Book


def test_read(books: list[Book]) -> None:
    """Через представление можно читать книги."""
    catalog = Catalog()
    catalog.add(books[1])
    catalog.add(books[0])

    view = catalog.read_only()

    assert view.get("001") == books[0]
    assert len(view) == 2
    assert "001" in view
    assert "missing" not in view
    assert list(view) == [books[0], books[1]]


def test_find(books: list[Book]) -> None:
    """Через представление работает поиск."""
    catalog = Catalog()
    for book in books:
        catalog.add(book)
    view = catalog.read_only()

    assert view.find_by_name("ДЮ") == (books[0],)
    assert view.find_by_name("Нет такой книги") == ()

    result = view.find_by_category("ФАНТАСТИКА")
    assert len(result) == 2
    assert books[0] in result
    assert books[1] in result


def test_live(books: list[Book]) -> None:
    """Изменения каталога сразу видны в представлении."""
    catalog = Catalog()
    view = catalog.read_only()
    assert len(view) == 0

    catalog.add(books[0])
    assert view.get("001") == books[0]
    assert len(view) == 1

    catalog.remove("001")
    assert "001" not in view
    assert len(view) == 0


def test_no_edit() -> None:
    """У представления нет методов изменения каталога."""
    view = Catalog().read_only()

    assert not hasattr(view, "add")
    assert not hasattr(view, "remove")
    assert not hasattr(view, "load")
    assert not hasattr(view, "undo")


def test_book_change(books: list[Book]) -> None:
    """Полученную книгу нельзя изменить."""
    catalog = Catalog()
    catalog.add(books[0])
    view = catalog.read_only()
    book = view.get("001")

    with pytest.raises(FrozenInstanceError):
        book.title = "Другое название"  # type: ignore[misc]
