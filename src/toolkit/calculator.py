import re
from decimal import Decimal

from . import constants, errors


def tokenize(expression: str) -> list[str]:
    """преобразование строки в удобный массив '1 +-23* 15.5' -> ['1', '+', '-', '23', '*', '15.5']"""

    expression_list = []
    temp_digits = ''
    char_position = 0

    while char_position < len(expression):

        char = expression[char_position]

        if char == ' ' or char == '\n' or char == '\t':
            if temp_digits != '':
                expression_list.append(temp_digits)
            temp_digits = ''
            char_position += 1
        elif char in constants.ALLOWED_SYMBOLS:
            if temp_digits != '':
                expression_list.append(temp_digits)
            temp_digits = ''
            if char == '/' and char_position < len(expression) - 1:
                if expression[char_position + 1] == '/':
                    expression_list.append("//")
                    char_position += 2
                    continue
            expression_list.append(char)
            char_position += 1
        elif char in constants.DIGITS or char == '.':
            temp_digits += char
            char_position += 1
        else:
            raise errors.InvalidExpressionError(f"Недопустимый символ '{char}' в строке.")

    if temp_digits != '':
        expression_list.append(temp_digits)

    return expression_list


def validate(expression_list: list[str]) -> bool:
    """Проверка корректности токенов в выражении"""

    if not expression_list:
        raise errors.InvalidExpressionError("Пустое выражение.")

    parentheses_balance = 0
    previous_token_type = "operand"

    if expression_list[0] == '(':
        previous_token_type = "open_paren"
        parentheses_balance += 1

    if '.' in expression_list:
        raise errors.InvalidNumberError("Одиночная точка не может находится в выражения.")

    if expression_list[-1] in constants.ALLOWED_SYMBOLS and expression_list[-1] != ')':
        raise errors.InvalidEndTokenError(f"Выражение заканчивается недопустимым токеном '{expression_list[-1]}'.")
    if expression_list[0] in constants.ALLOWED_SYMBOLS:
        if expression_list[0] not in constants.UNARY_OPERATORS and expression_list[0] != '(':
            raise errors.InvalidStartTokenError(f"Выражение начинается недопустимым токеном '{expression_list[0]}'.")
        elif expression_list[0] in constants.UNARY_OPERATORS:
            previous_token_type = "unary_operator"
    elif not re.fullmatch(r"[0-9]+(\.[0-9]+)?", expression_list[0]):
        raise errors.InvalidNumberError(f"Некорректный операнд '{expression_list[0]}'.")

    for token in expression_list[1:]:
        if token == '(':
            if previous_token_type in ["binary_operator", "unary_operator", "open_paren"]:
                parentheses_balance += 1
                previous_token_type = "open_paren"
            else:
                raise errors.ExpectedOperandError("Перед '(' пропущен оператор.")
        elif token == ')':
            if previous_token_type in ["operand", "close_paren"]:
                parentheses_balance -= 1
                if parentheses_balance < 0:
                    raise errors.UnbalancedParenthesesError("Скобка ')' должна стоять позже '('.")
                previous_token_type = "close_paren"
            else:
                raise errors.ExpectedOperandError("Перед ')' пропущен операнд.")
        elif token in constants.ALLOWED_SYMBOLS:
            if previous_token_type in ["operand", "close_paren"]:
                previous_token_type = "binary_operator"
            elif previous_token_type in ["binary_operator", "unary_operator", "open_paren"]:
                if token in constants.UNARY_OPERATORS:
                    previous_token_type = "unary_operator"
                else:
                    raise errors.ExpectedOperandError(f"После бинарного оператора получен не унарный, не число и не '(', а '{token}'.")
        elif re.fullmatch(r"[0-9]+(\.[0-9]+)?", token):
            if previous_token_type in ["binary_operator", "unary_operator", "open_paren"]:
                previous_token_type = "operand"
            else:
                raise errors.ExpectedOperandError("Между операндами пропущен оператор.")
        else:
            raise errors.InvalidNumberError(f"Некорректное число '{token}'.")

    if parentheses_balance > 0:
        raise errors.UnbalancedParenthesesError("Не хватает ')' после '('.")

    return True


def to_rpn(validated_expression: list[str], position: int = 0) -> tuple[list[str], int]:
    """Преобразование проверенного выражение в RPN вид."""

    rpn: list[str] = []
    operator_stack: list[str] = []
    expect_operand = True

    while position < len(validated_expression):
        token = validated_expression[position]

        if token not in constants.ALLOWED_SYMBOLS:
            rpn.append(token)
            expect_operand = False
        elif token == '(':
            new_rpn, position = to_rpn(validated_expression, position + 1)
            rpn.extend(new_rpn)
            expect_operand = False
            continue
        elif token == ')':
            while len(operator_stack) > 0:
                rpn.append(operator_stack[-1])
                operator_stack.pop(-1)
            return rpn, position + 1
        elif expect_operand:
            operator_stack.append(f"u{token}")
        else:
            while (
                len(operator_stack) > 0
                and constants.OPERATOR_PRECEDENCE[operator_stack[-1]]
                >= constants.OPERATOR_PRECEDENCE[token]
            ):
                rpn.append(operator_stack[-1])
                operator_stack.pop(-1)
            operator_stack.append(token)
            expect_operand = True

        position += 1

    while len(operator_stack) > 0:
        rpn.append(operator_stack[-1])
        operator_stack.pop(-1)

    return rpn, position


def calculation_rpn(rpn: list[str]) -> Decimal:
    """Вычисление через RPN."""

    stack: list[Decimal] = []

    for token in rpn:
        if token == "u+":
            continue
        if token == "u-":
            stack[-1] = -stack[-1]
        elif token in constants.ALLOWED_SYMBOLS:
            right = stack.pop(-1)
            left = stack.pop(-1)

            if token in ['/', '%', '//']:
                if right == 0:
                    raise errors.DivisionByZeroError("Нельзя делить на ноль.")
                elif left == 0:
                    stack.append(left)
                    continue

            match token:
                case '+':
                    stack.append(left + right)
                case '-':
                    stack.append(left - right)
                case '*':
                    stack.append(left * right)
                case '/':
                    stack.append(left / right)
                case '//':
                    if (left < 0) and left % right != 0:
                        stack.append(left // right - right / abs(right))
                    else:
                        stack.append(left // right)
                case '%':
                    if left < 0 and left % right != 0:
                        stack.append(left % right + abs(right))
                    else:
                        temp_result = left % right
                        stack.append(temp_result)

        else:
            stack.append(Decimal(token))

    if stack[0] == 0:
        return Decimal(0)
    return stack[0]
