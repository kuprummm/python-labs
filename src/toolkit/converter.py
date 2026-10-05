import json

from pathlib import Path
from . import errors, constants


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Перевод значений"""

    config_path = Path(__file__).with_name("conversions.json")

    with open(config_path, encoding="utf-8") as file:
        table = json.load(file)

    lower_from_unit = from_unit.lower()
    lower_to_unit = to_unit.lower()

    for unit in (lower_from_unit, lower_to_unit):
        if unit not in (set(table["mass"]) | set(table["length"]) | {'f', 'c', 'k'}):
            raise errors.UnknownUnitError(f"Неизвестная единица измерения '{unit}'.")

    if lower_from_unit in ['k', 'c', 'f']:
        if lower_to_unit in ['k', 'c', 'f']:
            result = convert_temperature(value, lower_from_unit, lower_to_unit)
        else:
            raise errors.IncompatibleUnitsError("Температуру можно переводить только в температуру.")
    elif lower_from_unit in table["mass"]:
        if lower_to_unit in table["mass"]:
            result = value * table["mass"][lower_from_unit] / table["mass"][lower_to_unit]
        else:
            raise errors.IncompatibleUnitsError("Массу можно переводить только в массу.")
    else:
        if lower_to_unit in table["length"]:
            result = value * table["length"][lower_from_unit] / table["length"][lower_to_unit]
        else:
            raise errors.IncompatibleUnitsError("Длинну можно переводить только в Длинну.")

    return result


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Перевод температур"""

    if value < constants.MINIMUM_TEMPERATURE[from_unit]:
        raise errors.BelowAbsoluteZeroError("Ниже абсолютного нуля.")

    if from_unit == to_unit:
        return value

    if from_unit == 'f' and to_unit == 'c':
        result = (value - 32) * 5 / 9
    elif from_unit == 'k' and to_unit == 'c':
        result = value - 273.15
    elif from_unit == 'c' and to_unit == 'f':
        result = value * 9 / 5 + 32
    elif from_unit == 'c' and to_unit == 'k':
        result = value + 273.15
    else:
        temp_result = convert_temperature(value, from_unit, 'c')
        result = convert_temperature(temp_result, 'c', to_unit)

    return result
