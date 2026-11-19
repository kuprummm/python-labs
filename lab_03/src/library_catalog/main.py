import sys

from .catalog import Catalog
from .cli import build_parser, run_shell
from .errors import CatalogError


def main() -> int:
    """Загрузить каталог и начать сессию."""
    args = build_parser().parse_args()

    try:
        catalog = Catalog()
        catalog.load(args.file)
        run_shell(catalog, args.file)

    except (CatalogError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    return 0
