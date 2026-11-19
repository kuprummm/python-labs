import pytest

from library_catalog.catalog import Catalog
from library_catalog.errors import (
    BookNotFoundedError,
    DoubleIDError,
    InvalidBookValueError,
)
from library_catalog.models import Book


def test_empty() -> None:
    """В новом каталоге нет книг."""
    catalog = Catalog()

    assert len(catalog) == 0
    assert tuple(catalog) == ()
    assert "001" not in catalog


def test_add(books: list[Book]) -> None:
    """Добавляем книгу и находим её по ID."""
    catalog = Catalog()
    catalog.add(books[0])

    assert catalog.get("001") == books[0]
    assert len(catalog) == 1
    assert "001" in catalog


def test_same_id(books: list[Book]) -> None:
    """Дважды добавить один ID нельзя."""
    catalog = Catalog()
    catalog.add(books[0])

    with pytest.raises(DoubleIDError):
        catalog.add(books[0])

    assert catalog.get("001") == books[0]
    assert len(catalog) == 1


def test_bad_book() -> None:
    """Строка не подходит вместо книги."""
    catalog = Catalog()

    with pytest.raises(InvalidBookValueError):
        catalog.add("Дюна")  # type: ignore[arg-type]

    assert len(catalog) == 0


def test_no_book() -> None:
    """Такого ID нет."""
    catalog = Catalog()

    with pytest.raises(BookNotFoundedError):
        catalog.get("missing")


def test_remove(books: list[Book]) -> None:
    """Удаляем книги и проверяем поиск по жанру."""
    catalog = Catalog()
    catalog.add(books[0])
    catalog.add(books[1])

    catalog.remove("001")

    assert "001" not in catalog
    assert catalog.find_by_category("Фантастика") == (books[1],)
    assert len(catalog) == 1

    catalog.remove("002")

    assert catalog.find_by_category("Фантастика") == ()
    assert len(catalog) == 0


def test_remove_missing() -> None:
    """Удалить отсутствующую книгу нельзя."""
    catalog = Catalog()

    with pytest.raises(BookNotFoundedError):
        catalog.remove("missing")


def test_category(books: list[Book]) -> None:
    """Находим обе фантастические книги."""
    catalog = Catalog()
    for book in books:
        catalog.add(book)

    result = catalog.find_by_category("ФАНТАСТИКА")

    assert len(result) == 2
    assert books[0] in result
    assert books[1] in result
    assert books[2] not in result


def test_no_category() -> None:
    """Неизвестный жанр ничего не находит."""
    catalog = Catalog()

    assert catalog.find_by_category("Неизвестный жанр") == ()


def test_name(books: list[Book]) -> None:
    """Ищем по началу названия."""
    catalog = Catalog()
    for book in books:
        catalog.add(book)

    assert catalog.find_by_name("ДЮ") == (books[0],)
    assert catalog.find_by_name("юна") == ()
    assert catalog.find_by_name("Нет такой книги") == ()


def test_bad_search() -> None:
    """Запрос должен быть строкой."""
    catalog = Catalog()

    with pytest.raises(InvalidBookValueError):
        catalog.find_by_name(123)  # type: ignore[arg-type]

    with pytest.raises(InvalidBookValueError):
        catalog.find_by_category(123)  # type: ignore[arg-type]


def test_has_id() -> None:
    """Число и список не подходят вместо ID."""
    catalog = Catalog()

    assert 123 not in catalog
    assert [] not in catalog


def test_order(books: list[Book]) -> None:
    """Книги идут по ID."""
    catalog = Catalog()
    catalog.add(books[1])
    catalog.add(books[0])

    assert list(catalog) == [books[0], books[1]]
    assert list(catalog) == [books[0], books[1]]


def test_result(books: list[Book]) -> None:
    """Очистка своего списка не удаляет книги из каталога."""
    catalog = Catalog()
    catalog.add(books[0])

    result = catalog.find_by_category("Фантастика")
    assert isinstance(result, tuple)
    result_list = list(result)
    result_list.clear()

    assert len(catalog) == 1
    assert catalog.get("001") == books[0]


def test_index_add(books: list[Book]) -> None:
    """В одном жанре могут быть две книги."""
    catalog = Catalog()
    for book in books:
        catalog.add(book)

    assert catalog._category["фантастика"] == {"001", "002"}
    assert catalog._category["роман"] == {"003"}


def test_index_remove(books: list[Book]) -> None:
    """При удалении книги убираем её ID из жанра."""
    catalog = Catalog()
    for book in books:
        catalog.add(book)

    catalog.remove("001")
    assert catalog._category["фантастика"] == {"002"}

    catalog.remove("002")
    assert "фантастика" not in catalog._category
    assert catalog._category["роман"] == {"003"}
