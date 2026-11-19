from dataclasses import dataclass

from .errors import InvalidBookValueError


@dataclass(frozen=True)
class Book:
    """Класс книги"""

    id: str
    title: str
    category: str
    year: int
    author: str
    pages: int

    def __post_init__(self) -> None:
        """Валидация полей класса."""

        if not isinstance(self.id, str) or not self.id.strip():
            raise InvalidBookValueError("ID должно быть непустой строкой.")
        if not isinstance(self.title, str) or not self.title.strip():
            raise InvalidBookValueError("Название должно быть непустой строкой.")
        if not isinstance(self.category, str) or not self.category.strip():
            raise InvalidBookValueError("Категория должна быть непустой строкой.")
        if not isinstance(self.author, str) or not self.author.strip():
            raise InvalidBookValueError("Автор должен быть непустой строкой.")

        if type(self.year) is not int or self.year <= 0:
            raise InvalidBookValueError("Год должен быть положительным целым числом.")
        if type(self.pages) is not int or self.pages <= 0:
            raise InvalidBookValueError(
                "Количество страниц должно быть положительным целым числом."
            )
