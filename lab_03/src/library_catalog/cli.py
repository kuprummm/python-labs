import argparse
import sys

from .catalog import Catalog
from .errors import CatalogError
from .models import Book


def build_parser() -> argparse.ArgumentParser:
    """Взаимодействие через cmd"""

    parser = argparse.ArgumentParser(description="Каталог книг")
    parser.add_argument("--file", default="library.json")

    return parser


def run_shell(catalog: Catalog, path: str) -> None:
    """Сессия для корректного undo."""

    print("Команды: list, get, add, remove, find-name, find-category, undo, exit")

    while True:
        try:
            command = input("Команда: ").strip().lower()

            if command == "list":
                for book in catalog:
                    print(f"ID: {book.id} | NAME: {book.title} | AUTHOR: {book.author}")

            elif command == "get":
                item_id = input("ID книги: ").strip()
                book = catalog.get(item_id)
                print(f"ID: {book.id}\nNAME: {book.title}\nAUTHOR: {book.author}")

            elif command == "add":
                item_id = input("ID книги: ").strip()
                title = input("Название: ").strip()
                category = input("Категория: ").strip()
                author = input("Автор: ").strip()
                year = int(input("Год: "))
                pages = int(input("Количество страниц: "))

                book = Book(
                    id=item_id,
                    title=title,
                    category=category,
                    year=year,
                    author=author,
                    pages=pages,
                )

                catalog.add(book)
                catalog.save(path)
                print("Книга успешно добавлена.")

            elif command == "remove":
                item_id = input("ID книги: ").strip()
                catalog.remove(item_id)
                catalog.save(path)
                print("Книга успешно удалена.")

            elif command == "find-name":
                title = input("Начало названия: ").strip()
                result = catalog.find_by_name(title)

                if not result:
                    print("Книги не найдены.")

                for book in result:
                    print(f"ID: {book.id} | NAME: {book.title} | AUTHOR: {book.author}")

            elif command == "find-category":
                category = input("Категория: ").strip()
                result = catalog.find_by_category(category)

                if not result:
                    print("Книги не найдены.")

                for book in result:
                    print(f"ID: {book.id} | NAME: {book.title} | AUTHOR: {book.author}")

            elif command == "undo":
                catalog.undo()
                catalog.save(path)
                print("Последнее действие отменено.")

            elif command == "exit":
                break

            elif command == "":
                continue

            else:
                print("Неизвестная команда.")

        except (CatalogError, OSError) as error:
            print(f"Ошибка: {error}", file=sys.stderr)

        except ValueError:
            print(
                "Ошибка: год и количество страниц нужно вводить целыми числами.",
                file=sys.stderr,
            )

        except (EOFError, KeyboardInterrupt):
            print("\nСессия завершена.")
            break
