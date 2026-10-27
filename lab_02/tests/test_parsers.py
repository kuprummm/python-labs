from pathlib import Path

import pytest

from streamstats import errors, parsers


def test_csv(tmp_path: Path) -> None:
    """Проверка чтения CSV."""
    path = tmp_path / "events.csv"
    path.write_text("timestamp,level,source,message\n2026-10-23T12:00:00Z,INFO,сайт,Запуск\n", encoding="utf-8")

    result = list(parsers.pars_csv(str(path), {"skipped": 0}))

    assert len(result) == 1
    assert result[0]["source"] == "сайт"
    assert result[0]["message"] == "Запуск"


def test_jsonl(tmp_path: Path) -> None:
    """Проверка чтения JSONL."""
    path = tmp_path / "events.jsonl"
    path.write_text('{"timestamp":"2026-10-23T12:00:00Z","level":"ERROR","source":"db","message":"Ошибка"}\n', encoding="utf-8")

    result = list(parsers.pars_jsonl(str(path), {"skipped": 0}))

    assert len(result) == 1
    assert result[0]["level"] == "ERROR"
    assert result[0]["source"] == "db"


def test_txt(tmp_path: Path) -> None:
    """Проверка собственного формата."""
    path = tmp_path / "events.txt"
    path.write_text("2026-10-23T12:00:00Z|INFO|site|Запуск\n", encoding="utf-8")

    result = list(parsers.pars_custom_format(str(path), {"skipped": 0}))

    assert len(result) == 1
    assert result[0]["message"] == "Запуск"


def test_empty_file(tmp_path: Path) -> None:
    """Проверка пустого файла."""
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    assert list(parsers.pars_custom_format(str(path), {"skipped": 0})) == []


def test_csv_error(tmp_path: Path) -> None:
    """Проверка ошибки CSV."""
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,level,source,message\n2026-10-23T12:00:00Z,BAD,site,Тест\n", encoding="utf-8")

    with pytest.raises(errors.InvalidParsEvent) as error_info:
        list(parsers.pars_csv(str(path), {"skipped": 0}))

    assert "строке 2" in str(error_info.value)


def test_jsonl_error(tmp_path: Path) -> None:
    """Проверка неправильного JSON."""
    path = tmp_path / "bad.jsonl"
    path.write_text("{broken\n", encoding="utf-8")

    with pytest.raises(errors.InvalidParsEvent):
        list(parsers.pars_jsonl(str(path), {"skipped": 0}))


def test_jsonl_not_dictionary(tmp_path: Path) -> None:
    """JSON-запись должна быть словарём."""
    path = tmp_path / "bad.jsonl"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(errors.InvalidParsEvent):
        list(parsers.pars_jsonl(str(path), {"skipped": 0}))


def test_txt_error(tmp_path: Path) -> None:
    """В записи должно быть четыре поля."""
    path = tmp_path / "bad.txt"
    path.write_text("time|INFO|site\n", encoding="utf-8")

    with pytest.raises(errors.InvalidParsEvent):
        list(parsers.pars_custom_format(str(path), {"skipped": 0}))


def test_invalid_date(tmp_path: Path) -> None:
    """Проверка неправильной даты в записи."""
    path = tmp_path / "bad.txt"
    path.write_text("wrong|INFO|site|Запуск\n", encoding="utf-8")

    with pytest.raises(errors.InvalidParsEvent):
        list(parsers.pars_custom_format(str(path), {"skipped": 0}))


def test_csv_skip_invalid(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Пропуск ошибки и продолжение чтения CSV."""
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,level,source,message\n2026-10-23T12:00:00Z,BAD,site,Ошибка\n2026-10-23T12:01:00Z,INFO,site,Запуск\n", encoding="utf-8")
    stats = {"skipped": 0}

    result = list(parsers.pars_csv(str(path), stats, skip_invalid=True))

    assert len(result) == 1
    assert stats["skipped"] == 1
    assert caplog.text != ""


def test_jsonl_skip_invalid(tmp_path: Path) -> None:
    """Пропуск неправильной строки JSONL."""
    path = tmp_path / "bad.jsonl"
    path.write_text('{broken\n{"timestamp":"2026-10-23T12:00:00Z","level":"INFO","source":"site","message":"Запуск"}\n', encoding="utf-8")
    stats = {"skipped": 0}

    result = list(parsers.pars_jsonl(str(path), stats, skip_invalid=True))

    assert len(result) == 1
    assert stats["skipped"] == 1


def test_txt_skip_invalid(tmp_path: Path) -> None:
    """Пропуск неправильной строки TXT."""
    path = tmp_path / "bad.txt"
    path.write_text("time|INFO|site\n2026-10-23T12:00:00Z|INFO|site|Запуск\n", encoding="utf-8")
    stats = {"skipped": 0}

    result = list(parsers.pars_custom_format(str(path), stats, skip_invalid=True))

    assert len(result) == 1
    assert stats["skipped"] == 1
