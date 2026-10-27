import sys
import argparse

from decimal import Decimal

from . import calculator, converter, history


def main() -> int:
    """Разорать аргументы и выполнить выбранную команду с разобраными аргументами"""

    parser = argparse.ArgumentParser(description="Калькулятор и конвертер")

    commands = parser.add_subparsers(dest="command", required=True)

    calc = commands.add_parser("calc")
    calc.add_argument("expression")

    convert = commands.add_parser("convert")
    convert.add_argument("value", type=float)
    convert.add_argument("--from", dest="from_unit", required=True)
    convert.add_argument("--to", dest="to_unit", required=True)

    args = parser.parse_args()

    result: Decimal | float

    try:
        if args.command == "calc":
            tokens = calculator.tokenize(args.expression)
            calculator.validate(tokens)
            rpn, pos = calculator.to_rpn(tokens)
            result = calculator.calculation_rpn(rpn)
            history.save_calculate(args.expression, result)
        else:
            result = converter.convert(args.value, args.from_unit, args.to_unit)
    except (ValueError, ZeroDivisionError) as error:
        print(str(error), file=sys.stderr)
        return 2


    print(result)
    return 0
