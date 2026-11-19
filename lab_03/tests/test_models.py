from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from library_catalog.errors import InvalidBookValueError
from library_catalog.models import Book


def test_book(books: list[Book]) -> None:
    """Проверяем поля книги."""
    book = books[0]

    assert book.id == "001"
    assert book.title == "Дюна"
    assert book.category == "Фантастика"
    assert book.year == 1965
    assert book.author == "Фрэнк Герберт"
    assert book.pages == 600


def test_no_title(bad_fields: dict[str, Any]) -> None:
    """Название пустое."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["no_title"])


def test_no_id(bad_fields: dict[str, Any]) -> None:
    """В ID только пробелы."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["no_id"])


def test_no_category(bad_fields: dict[str, Any]) -> None:
    """Жанр пустой."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["no_category"])


def test_no_author(bad_fields: dict[str, Any]) -> None:
    """Автор пустой."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["no_author"])


def test_bad_year(bad_fields: dict[str, Any]) -> None:
    """Год равен нулю."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["bad_year"])


def test_bad_pages(bad_fields: dict[str, Any]) -> None:
    """Страниц меньше нуля."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["bad_pages"])


def test_bool_pages(bad_fields: dict[str, Any]) -> None:
    """True нельзя записать вместо числа страниц."""
    with pytest.raises(InvalidBookValueError):
        Book(**bad_fields["bool_pages"])


def test_change(books: list[Book]) -> None:
    """Поля книги менять нельзя."""
    book = books[0]

    with pytest.raises(FrozenInstanceError):
        book.title = "Другое название"  # type: ignore[misc]
