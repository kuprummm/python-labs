from collections.abc import Iterator

from .errors import (
    BookNotFoundedError,
    DoubleIDError,
    HistoryError,
    InvalidBookValueError,
)
from .models import Book
from .storage import read_books, write_books


class Catalog:
    """Класс каталога"""

    def __init__(self) -> None:
        """Создать пустой каталог книг и категории."""

        self._books: dict[str, Book] = {}
        self._category: dict[str, set[str]] = {}
        self._history: list[tuple[str, Book]] = []

    def add(self, item: Book) -> None:
        """Добавление новой книги в каталог."""

        if not isinstance(item, Book):
            raise InvalidBookValueError("Переданный объект не книга.")
        if item.id in self._books:
            raise DoubleIDError("Книга с таким ID уэе есть.")

        self._books[item.id] = item
        book_category = item.category.lower()
        if book_category not in self._category:
            self._category[book_category] = set()

        self._category[book_category].add(item.id)
        self._history.append(("add", item))

    def get(self, item_id: str) -> Book:
        """Получение книги по айди"""

        if item_id not in self._books:
            raise BookNotFoundedError("Книга с таким айди не найдена.")

        return self._books[item_id]

    def remove(self, item_id: str) -> None:
        """Удаление книги по айди."""

        if item_id not in self._books:
            raise BookNotFoundedError("Книга с таким айди не найдена.")

        book = self.get(item_id)
        book_category = book.category.lower()
        self._category[book_category].remove(item_id)

        if len(self._category[book_category]) == 0:
            self._category.pop(book_category)

        self._books.pop(item_id)
        self._history.append(("remove", book))

    def find_by_category(self, category: str) -> tuple[Book, ...]:
        """Поиск книг по категории."""

        if not isinstance(category, str):
            raise InvalidBookValueError("Категория должна быть строкой.")

        category_lower = category.lower()
        book_list: list[Book] = []

        if category_lower in self._category:
            for book_id in self._category[category_lower]:
                book_list.append(self._books[book_id])

        return tuple(book_list)

    def find_by_name(self, title: str) -> tuple[Book, ...]:
        """Поиск книг по началу названия."""

        if not isinstance(title, str):
            raise InvalidBookValueError("Часть названия должна быть строкой")

        title_lower = title.lower()
        book_list: list[Book] = []

        for books_id in self._books:
            book = self.get(books_id)
            if book.title.lower().startswith(title_lower):
                book_list.append(book)

        return tuple(book_list)

    def __len__(self) -> int:
        """Получение кол-ва книг."""

        return len(self._books)

    def __contains__(self, item_id: object) -> bool:
        """Проверка наличия кннги по айди."""

        if not isinstance(item_id, str):
            return False

        return item_id in self._books

    def __iter__(self) -> Iterator[Book]:
        """Перебор книг"""

        for book_id in sorted(self._books):
            book = self.get(book_id)
            yield book

    def save(self, path: str) -> None:
        write_books(path, self)

    def load(self, path: str) -> None:
        """Загрузить каталог."""

        loaded_books = read_books(path)

        new_catalog = Catalog()

        for book in loaded_books:
            new_catalog.add(book)

        self._books = new_catalog._books
        self._category = new_catalog._category
        self._history.clear()

    def undo(self) -> None:
        """Отмена последнего действия."""

        if len(self._history) == 0:
            raise HistoryError("Отменять нечего.")

        action, book = self._history[-1]

        if action == "add":
            item_id = book.id
            if item_id not in self._books:
                raise BookNotFoundedError("Книга с таким айди не найдена.")

            book = self.get(item_id)
            book_category = book.category.lower()
            self._category[book_category].remove(item_id)

            if len(self._category[book_category]) == 0:
                self._category.pop(book_category)

            self._books.pop(item_id)

            self._history.pop(-1)
        elif action == "remove":
            if book.id in self._books:
                raise DoubleIDError("Книга с таким ID уэе есть.")

            self._books[book.id] = book
            book_category = book.category.lower()
            if book_category not in self._category:
                self._category[book_category] = set()

            self._category[book_category].add(book.id)

            self._history.pop(-1)

    def read_only(self):
        """Получить каталог только для чтения."""

        return ReadOnlyCatalog(self)


class ReadOnlyCatalog:
    """Каталог только для чтения."""

    def __init__(self, catalog: Catalog) -> None:
        """СОздание конструктора."""
        self._catalog = catalog

    def get(self, item_id: str) -> Book:
        return self._catalog.get(item_id)

    def find_by_name(self, title: str) -> tuple[Book, ...]:
        return self._catalog.find_by_name(title)

    def find_by_category(self, category: str) -> tuple[Book, ...]:
        return self._catalog.find_by_category(category)

    def __len__(self) -> int:
        return len(self._catalog)

    def __iter__(self) -> Iterator[Book]:
        return self._catalog.__iter__()

    def __contains__(self, item_id: object) -> bool:
        return item_id in self._catalog
