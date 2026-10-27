# 1

Лабораторная работа номер 2

Амелькин Евгений МО-102бв-26

Программа для подсчёта статистики по логам.

# 2 Что умеет

- Читать файлы CSV, JSONL и TXT.
- Обрабатывать несколько файлов за один запуск.
- Проверять записи и сообщать об ошибках.
- Считать события по уровням и источникам.
- Показывать пять источников с наибольшим количеством ошибок.
- Находить первую и последнюю дату.
- Выбирать события по уровню, источнику и времени.
- Сохранять результат в JSON.

Файл читается постепенно. Все записи сразу в память не загружаются.

# 3 Установка

Скачать проект:

```cmd
git clone https://github.com/kuprummm/python-labs.git
cd python-labs
```

Создание окружения:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Установка:

```cmd
python -m pip install -r lab_02/requirements.txt
python -m pip install -r lab_02/requirements-tests.txt
python -m pip install -e ./lab_02
```

# 4 Запуск

```cmd
python -m streamstats --help
python -m streamstats analyze --help
```
Виды парсерос:

1) CSV:

```cmd
python -m streamstats analyze lab_02/example/events.csv --format csv --output report.json
```

2) JSONL:

```cmd
python -m streamstats analyze lab_02/example/events.jsonl --format jsonl --output report.json
```

3) TXT:

```cmd
python -m streamstats analyze lab_02/example/events.txt --format txt --output report.json
```

Несколько файлов:

```cmd
python -m streamstats analyze first.jsonl second.jsonl --format jsonl --output report.json
```

Входные файлы должны быть одного формата.

По умолчанию `--output` = `report.json`.

Если в пути пробелы берем путь в кавычки.

# 5 Что должно быть в файле

В каждой строке события 4 обязательных поля:

- `timestamp` - дата и время.
- `level` - уровень события.
- `source` - источник.
- `message` - сообщение.

Допустимые уровни (меняются в constants.py): `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

CSV: Первая строка - названия полей:

```csv
timestamp,level,source,message
2026-10-23T12:00:00+03:00,INFO,website,Сайт запущен
2026-10-23T12:01:00+03:00,ERROR,database,Ошибка подключения
```

Если в сообщении есть запятая сообщение нужно заключить в двойные кавычки.

JSONL: Каждая запись занимает только одну строку:

```jsonl
{"timestamp":"2026-10-23T12:00:00+03:00","level":"INFO","source":"website","message":"Сайт запущен"}
{"timestamp":"2026-10-23T12:01:00+03:00","level":"ERROR","source":"database","message":"Ошибка подключения"}
```

Пользовательский TXT-формата. Заголовка нет поля разделены - `|`:

```text
2026-10-23T12:00:00+03:00|INFO|website|Сайт запущен
2026-10-23T12:01:00+03:00|ERROR|database|Ошибка подключения
```

В TXT должно быть ровно четыре поля. Внутри значений знак `|` использовать нельзя.

# 6 Фильтры и время

фильтр по `database` и `ERROR`.

```cmd
python -m streamstats analyze lab_02/example/events.csv --format csv --level ERROR --source database --output filtered.json
```

по времени от `start-time` до `last-time` (любой их них может быть по одиночному None (не указан)):

```cmd
python -m streamstats analyze lab_02/example/events.csv --format csv --start-time "2026-10-23T12:01:00+03:00" --last-time "2026-10-23T12:03:00+03:00" --output filtered.json
```

Примеры времени:

- `2026-10-23T12:00:00+03:00` - с часовым поясом.
- `2026-10-23T09:00:00Z` - время по UTC.
- `2026-10-23T09:00:00` - без пояса - будет считаться UTC.
- `2026-10-23` - эквиваленотна `2026-10-23T00:00:00`.

# 7 Ошибки

Без `--skip-invalid` программа останавливается на первой ошибке записи и сообщает файл, строку и причину.

Для продолжение при встречи ошибки:

```cmd
python -m streamstats analyze lab_02/example/br.txt --format txt --skip-invalid --output report.json
```

Программа выводит предупреждение и продолжает работу. Количество пропущенных записей сохраняется.

Коды завершения:

- `0` - программа выполнила работу.
- `2` - ошибка.

Сообщения об ошибках и предупреждения выводятся в `stderr`.

# 8 Что будет в отчёте

- `total` - количество подходящих коректных событий.
- `by_level` - количество по уровням.
- `by_source` - количество по источникам.
- `top_error_sources` - топ 5 источников `ERROR` и `CRITICAL`.
- `first_time` и `last_time` - дата начала и конца.
- `skipped` - пропущенные записи из за ошибок.

При одинаковом количестве ошибок источники идут по алфавиту.

Если событий нет, счётчики равны нулю, источники и топ пустые, даты - `null`.

# 9 Бонусы

- Фильтры по уровню, источнику и времени.
- Свой TXT-формат и словарь `PARSERS` для выбора парсера.
- Проверка памяти на большом файле.

# Тесты

Запуск:

```bash
python -m pytest -v
```

Покрытие - 84.23%
