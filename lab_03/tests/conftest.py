import json
from pathlib import Path
from typing import Any

import pytest

from library_catalog.models import Book


@pytest.fixture
def examples() -> Path:
    """Папка с готовыми файлами."""
    return Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture
def books(examples: Path) -> list[Book]:
    """Три книги из books.json."""
    with open(examples / "books.json", encoding="utf-8") as file:
        data = json.load(file)

    # ** передаёт поля словаря в Book: id, title, category и остальные.
    return [Book(**book) for book in data["books"]]


@pytest.fixture
def bad_fields(examples: Path) -> dict[str, Any]:
    """Готовые примеры с ошибками в полях."""
    with open(examples / "bad_fields.json", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return data
