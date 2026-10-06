import pytest
import sys

from toolkit import cli


def test_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверить успешный вывод справки."""
    monkeypatch.setattr(sys, "argv", ["toolkit", "--help"])

    with pytest.raises(SystemExit) as exit_info:
        cli.main()

    assert exit_info.value.code == 0


def test_cli_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка в stderr и код завершения 2."""

    monkeypatch.setattr(sys, "argv", ["toolkit", "calc", "2/0"])

    exit_code = cli.main()
    output = capsys.readouterr()

    assert exit_code == 2
    assert output.err != ""
    assert output.out == ""
