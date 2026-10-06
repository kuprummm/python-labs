import json
from decimal import Decimal
from pathlib import Path


def save_calculate(exprission: str, result: Decimal) -> None:
    """Добавить успешное вычесление в историю."""

    history_path = Path("history.json")

    if history_path.exists():
        with history_path.open(encoding="utf-8") as file:
            history = json.load(file)

    else:
        history = []

    history.append({
        "expression": exprission,
        "result": str(result),
    })

    with history_path.open("w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)
