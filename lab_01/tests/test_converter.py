import pytest

from toolkit import converter, errors


def test_mm_to_m() -> None:
    """Перевод из мм в м."""
    assert converter.convert(200.0, "mm", 'm') == pytest.approx(0.2)


def test_kg_to_g() -> None:
    """Перевод из кг в г без учета регистра."""
    assert converter.convert(4.3, "Kg", "G") == pytest.approx(4300)


def test_c_to_f() -> None:
    """Перевод из С в Ф."""
    assert converter.convert(5.0, "c", "f") == pytest.approx(41.0)


def test_absolutely_zero() -> None:
    """Получение абсолютного нуля."""
    assert converter.convert(-273.15, "c", 'k') == pytest.approx(0.0)


def test_below_adsolutely_zero() -> None:
    """Температура ниже абсолютного нуля."""
    with pytest.raises(errors.BelowAbsoluteZeroError):
        converter.convert(-276, 'c', 'k')


def test_different_unit() -> None:
    """Проверка разных групп."""
    with pytest.raises(errors.IncompatibleUnitsError):
        converter.convert(5, 'm', 'kg')


def test_unknown_unit() -> None:
    """Неизвестная величина."""
    with pytest.raises(errors.UnknownUnitError):
        converter.convert(12, 'g', 'a')
