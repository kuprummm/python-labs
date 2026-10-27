import json
import sys
from pathlib import Path

import pytest

from streamstats import cli


def test_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверить успешный вывод справки."""
    monkeypatch.setattr(sys, "argv", ["streamstats", "--help"])

    with pytest.raises(SystemExit) as exit_info:
        cli.main()

    assert exit_info.value.code == 0


def test_cli_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка в stderr и код завершения 2."""
    path = tmp_path / "bad.txt"
    path.write_text("2026-10-23T12:00:00Z|BAD|site|Ошибка\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["streamstats", "analyze", str(path), "--format", "txt"])

    exit_code = cli.main()
    output = capsys.readouterr()

    assert exit_code == 2
    assert output.err != ""
    assert output.out == ""


def test_cli_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка отчёта по нескольким файлам."""
    first = tmp_path / "one.txt"
    second = tmp_path / "two.txt"
    first.write_text("2026-10-23T12:00:00Z|INFO|site|Запуск\n", encoding="utf-8")
    second.write_text("2026-10-23T12:01:00Z|ERROR|site|Ошибка\n", encoding="utf-8")
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["streamstats", "analyze", str(first), str(second), "--format", "txt", "--output", str(output)])

    exit_code = cli.main()
    result = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert result["total"] == 2
    assert result["by_source"] == {"site": 2}
    assert result["skipped"] == 0


def test_cli_skip_invalid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка флага пропуска ошибок."""
    path = tmp_path / "bad.txt"
    path.write_text("wrong\n2026-10-23T12:00:00Z|INFO|site|Запуск\n", encoding="utf-8")
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["streamstats", "analyze", str(path), "--format", "txt", "--skip-invalid", "--output", str(output)])

    exit_code = cli.main()
    result = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert result["total"] == 1
    assert result["skipped"] == 1
