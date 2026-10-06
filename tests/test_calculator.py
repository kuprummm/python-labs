from decimal import Decimal

import pytest

from toolkit import calculator, errors


def calculate(expression: str) -> Decimal:
    """Вычисляем результат переданного теста."""

    tokens = calculator.tokenize(expression)
    calculator.validate(tokens)
    rpn, pos = calculator.to_rpn(tokens)
    result = calculator.calculation_rpn(rpn)

    return result


def test_operator_precedence() -> None:
    """Проверка приорететов операторов."""
    assert calculate("2 + 3 * 4 / 2") == Decimal(8)


def test_fractional_division() -> None:
    """Проверка нецелого деления."""
    assert calculate("5 / 2") == Decimal(2.5)


def test_onece_unary() -> None:
    """Проверка унарного знака."""
    assert calculate("5 *- 2") == Decimal(-10)


def test_twice_unary() -> None:
    """Проверка унарногых знака."""
    assert calculate("5 *-+ 2") == Decimal(-10)


def test_bigspace() -> None:
    """ПРоверка табуляций и переносов."""
    assert calculate("3 -\n3 +\t 1") == Decimal(1)


def test_bonus_func_division() -> None:
    """Проверка целочисленного деления математического поведения."""
    assert calculate("-7 // 3") == Decimal(-3)


def test_bonus_func_remainder() -> None:
    """Проверка остатка от деления математического поведения."""
    assert calculate("-7 % 3") == Decimal(2)


def test_empty_expression() -> None:
    """Проверка пустого выражения."""
    with pytest.raises(errors.InvalidExpressionError):
        calculate("")


def test_repeating_binary_operators() -> None:
    """Проверка двойных бинарных операторов."""
    with pytest.raises(errors.InvalidExpressionError):
        calculate("3 *% 2")


def test_invalid_character() -> None:
    """Проверка недопустимого символа."""
    with pytest.raises(errors.InvalidExpressionError):
        calculate("4 - a")


def test_division_by_zero() -> None:
    """Проверка деления на ноль."""
    with pytest.raises(errors.DivisionByZeroError):
        calculate("10 / 0")
