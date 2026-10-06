class InvalidExpressionError(ValueError):
    """Некорректные выражения."""


class UnbalancedParenthesesError(InvalidExpressionError):
    """Нарушен баланс скобок."""


class InvalidStartTokenError(InvalidExpressionError):
    """Выражение начинается с недопустимого токена."""


class InvalidEndTokenError(InvalidExpressionError):
    """Выражение заканчивается недопустимым токеном."""


class InvalidNumberError(InvalidExpressionError):
    """Некорректная запись числа."""


class ExpectedOperandError(InvalidExpressionError):
    """Некорректная последовательность операндов."""


class DivisionByZeroError(ZeroDivisionError):
    """Деление на ноль."""


class IncompatibleUnitsError(ValueError):
    """Попытка перевода между разными группами величин."""


class UnknownUnitError(ValueError):
    """Указана неизвестная единица измерения."""


class BelowAbsoluteZeroError(ValueError):
    """Температура ниже абсолютного нуля."""
