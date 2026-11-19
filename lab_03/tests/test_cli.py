import sys
from pathlib import Path
from shutil import copyfile

import pytest

from library_catalog.main import main
from library_catalog.models import Book
from library_catalog.storage import read_books


def enter(monkeypatch: pytest.MonkeyPatch, commands: list[str]) -> None:
    """Передаём ответы вместо ручного ввода в терминале."""
    answers = iter(commands)

    def answer(prompt: str) -> str:
        """При каждом input берём следующий ответ."""
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)


def test_help(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Справка показывает аргумент file."""
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--help"])

    with pytest.raises(SystemExit) as result:
        main()

    assert result.value.code == 0
    assert "--file" in capsys.readouterr().out


def test_read(
    examples: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Показываем все книги и одну книгу по ID."""
    path = examples / "books.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(monkeypatch, ["list", "get", "001", "exit"])

    assert main() == 0

    output = capsys.readouterr()
    assert "Дюна" in output.out
    assert "Солярис" in output.out
    assert "ID: 001\nNAME: Дюна" in output.out
    assert output.err == ""


def test_add(
    examples: Path,
    tmp_path: Path,
    books: list[Book],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Вводим книгу и проверяем сохранённый файл."""
    path = tmp_path / "books.json"
    copyfile(examples / "empty.json", path)
    book = books[0]
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(
        monkeypatch,
        [
            "add",
            book.id,
            book.title,
            book.category,
            book.author,
            str(book.year),
            str(book.pages),
            "exit",
        ],
    )

    assert main() == 0

    assert read_books(str(path)) == (book,)
    assert "Книга успешно добавлена." in capsys.readouterr().out


def test_remove_undo(
    examples: Path,
    tmp_path: Path,
    books: list[Book],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Удаляем книгу и возвращаем её через undo."""
    path = tmp_path / "books.json"
    copyfile(examples / "books.json", path)
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(monkeypatch, ["remove", "001", "undo", "exit"])

    assert main() == 0

    assert read_books(str(path)) == tuple(books)
    output = capsys.readouterr()
    assert "Книга успешно удалена." in output.out
    assert "Последнее действие отменено." in output.out
    assert output.err == ""


def test_find(
    examples: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ищем по названию и жанру, в том числе без совпадений."""
    path = examples / "books.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(
        monkeypatch,
        [
            "find-name",
            "ДЮ",
            "find-category",
            "ФАНТАСТИКА",
            "find-name",
            "Нет такой книги",
            "find-category",
            "Нет такого жанра",
            "exit",
        ],
    )

    assert main() == 0

    output = capsys.readouterr()
    assert "Дюна" in output.out
    assert "Солярис" in output.out
    assert output.out.count("Книги не найдены.") == 2
    assert output.err == ""


def test_bad_commands(
    examples: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """После неправильной команды и ошибки сессия продолжается."""
    path = examples / "books.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(monkeypatch, ["", "wrong", "get", "missing", "undo", "list", "exit"])

    assert main() == 0

    output = capsys.readouterr()
    assert "Неизвестная команда." in output.out
    assert "Дюна" in output.out
    assert "Книга с таким айди не найдена." in output.err
    assert "Отменять нечего." in output.err


def test_bad_number(
    examples: Path,
    books: list[Book],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Буквы вместо года показывают ошибку и не закрывают сессию."""
    path = examples / "books.json"
    book = books[0]
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])
    enter(
        monkeypatch,
        [
            "add",
            book.id,
            book.title,
            book.category,
            book.author,
            "не число",
            "exit",
        ],
    )

    assert main() == 0

    assert "целыми числами" in capsys.readouterr().err


def test_no_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Если файла нет, программа возвращает код 2."""
    path = tmp_path / "missing.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])

    assert main() == 2

    assert "Ошибка:" in capsys.readouterr().err
    assert not path.exists()


def test_bad_file(
    examples: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Со сломанным JSON сессия не запускается."""
    path = examples / "bad_json.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])

    assert main() == 2

    assert "Некорректный JSON." in capsys.readouterr().err


def test_end(
    examples: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Конец ввода закрывает сессию."""
    path = examples / "books.json"
    monkeypatch.setattr(sys, "argv", ["library_catalog", "--file", str(path)])

    def stop(prompt: str) -> str:
        """Ввод закончился."""
        raise EOFError

    monkeypatch.setattr("builtins.input", stop)

    assert main() == 0

    assert "Сессия завершена." in capsys.readouterr().out
