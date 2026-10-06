ALLOWED_SYMBOLS = frozenset({'+', '-', '/', '*', '%', '(', ')', '//'})
UNARY_OPERATORS = frozenset({'+', '-'})
DIGITS = '1234567890'
OPERATOR_PRECEDENCE = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "//": 2,
    "%": 2,
    "u+": 3,
    "u-": 3,
}
MINIMUM_TEMPERATURE = {"c": -273.15, "f": -459.67, "k": 0.0}
