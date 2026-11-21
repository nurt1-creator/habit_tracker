# Habit Tracker — Documentation

Справочная документация по проекту: архитектура, классы, база данных и ключевые концепции Python/ООП, применённые в коде.

## Содержание

- [Запуск проекта](#запуск-проекта)
- [Архитектура](#архитектура)
- [Модуль enums](#модуль-enums)
- [Модуль exceptions](#модуль-exceptions)
- [Класс Habit](#класс-habit)
- [Класс HabitLog](#класс-habitlog)
- [Класс HabitLogRepository](#класс-habitlogrepository)
- [Класс User](#класс-user)
- [Консольный интерфейс](#консольный-интерфейс)
- [База данных](#база-данных)
- [Тесты](#тесты)
- [Справочник концепций](#справочник-концепций)
- [Roadmap](#roadmap)

---

## Запуск проекта

```bash
uv sync
docker compose up -d        # PostgreSQL (нужен только для работы с БД)
uv run -m app.cli           # консольное приложение
uv run pytest -v            # тесты
```

Запуск всегда из корня проекта (`habit_tracker/`), не из папки `app/`, и через `-m`. Причина — см. [Импорты и запуск как модуля](#импорты-и-запуск-как-модуля).

`app/main.py` сейчас — временный скрипт для экспериментов с БД (вставка и чтение через `Session`), не точка входа приложения.

## Архитектура

```
habit_tracker/
├── app/
│   ├── __init__.py
│   ├── enums.py         # HabitStatus, HabitFrequency
│   ├── exceptions.py    # HabitArchivedError, DuplicateLogError, DuplicateHabitError
│   ├── models.py        # Habit, HabitLog (доменные модели)
│   ├── repository.py    # HabitLogRepository (в памяти)
│   ├── user.py          # User
│   ├── cli.py           # консольный интерфейс (rich)
│   ├── database.py      # engine, Base, init_db()
│   ├── db_models.py     # HabitRecord (ORM-модель)
│   └── main.py          # временный скрипт для проверки БД
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_repository.py
│   └── test_user.py
├── docker-compose.yml   # PostgreSQL 16
├── pyproject.toml
├── README.md
├── DOCS.md
└── .gitignore
```

Слои ответственности:

| Слой | Отвечает за |
|---|---|
| `models.py` | Сущности предметной области и их правила валидации |
| `repository.py` | Хранение `HabitLog` (пока в памяти) и операции над ними: дубликаты, streak, статистика |
| `user.py` | Владение привычками, уникальность названий в рамках пользователя |
| `enums.py` | Фиксированные наборы допустимых значений |
| `exceptions.py` | Доменные ошибки — нарушения бизнес-правил |
| `cli.py` | Ввод/вывод в консоли; в моделях нет `input()`/`print()` |
| `database.py` | Подключение к БД и базовый класс ORM |
| `db_models.py` | Описание таблиц (только структура, без бизнес-логики) |

`Habit` намеренно **не знает** о своём владельце (`User`) — связь односторонняя `User → Habit`. Доменные классы и ORM-модели **разделены** сознательно: домен не зависит от способа хранения.

---

## Модуль enums

### `HabitStatus`

| Значение | Смысл |
|---|---|
| `ACTIVE` | Привычка активна, можно отмечать выполнение |
| `ARCHIVED` | Привычка в архиве, отметки запрещены |

### `HabitFrequency`

| Значение | Смысл |
|---|---|
| `EVERYDAY` | Ежедневная привычка |
| `EVERYWEEK` | Еженедельная привычка (в конкретный день недели) |

---

## Модуль exceptions

| Исключение | Выбрасывается, когда |
|---|---|
| `HabitArchivedError` | Попытка создать `HabitLog` для архивной привычки |
| `DuplicateLogError` | Попытка отметить одну привычку дважды за одну дату |
| `DuplicateHabitError` | Попытка добавить пользователю привычку с уже занятым названием |

Доменные исключения вместо `ValueError`/`Exception` — там, где ошибка отражает **нарушение бизнес-правила**: их можно ловить отдельно.

---

## Класс `Habit`

Представляет привычку пользователя.

### Поля

| Поле | Тип | Доступ | Правило |
|---|---|---|---|
| `name` | `str` | read/write | Не пустое и не из пробелов; пробелы по краям обрезаются |
| `description` | `str` | read/write | Пробелы по краям обрезаются |
| `frequency` | `HabitFrequency` | read/write | Проверка `isinstance`, иначе `TypeError` |
| `weekday` | `int \| None` | read-only | `None` для `EVERYDAY`; обязателен и `0–6` для `EVERYWEEK` (0 = понедельник, как `date.weekday()`) |
| `status` | `HabitStatus` | read-only | Меняется только через `archive()` / `activate()` |
| `created_at` | `date` | read-only | Выставляется при создании, неизменяем |

### Порядок проверок в `__init__`

1. `check_empty_name(name)`
2. `check_correct_freq_enum(frequency)` — сначала убеждаемся, что `frequency` вообще валиден
3. `check_weekday_consistency(frequency, weekday)` — только потом проверяем согласованность с `weekday`

Так сообщение об ошибке всегда указывает на первую реальную причину. Принцип: сначала все проверки, потом присваивания.

```python
Habit("X", "", HabitFrequency.EVERYDAY, weekday=2)
# ValueError: EVERYDAY не может иметь weekday

Habit("X", "", HabitFrequency.EVERYWEEK)
# ValueError: EVERYWEEK требует weekday

Habit("X", "", HabitFrequency.EVERYWEEK, weekday=10)
# IndexError: weekday вне диапазона 0-6
```

`weekday` — read-only: setter потребовал бы повторять проверку согласованности с `frequency`.

### Методы

- **`archive() -> None`** — статус `ARCHIVED`
- **`activate() -> None`** — статус `ACTIVE`

---

## Класс `HabitLog`

Факт выполнения привычки в конкретную дату. Хранит прямую ссылку на `Habit` (композиция).

| Поле | Тип | Правило |
|---|---|---|
| `habit` | `Habit` | Привычка должна быть активна на момент создания лога (`HabitArchivedError`) |
| `completed_date` | `date` | Не в будущем (`ValueError`) |

Проверка «нельзя дважды за день» не входит в `HabitLog` — она требует сравнения с другими логами и живёт в `HabitLogRepository`.

---

## Класс `HabitLogRepository`

Хранилище `HabitLog` (список в памяти) и анализ истории выполнения.

#### `add(log: HabitLog) -> None`

Добавляет лог. `DuplicateLogError`, если для привычки с тем же `name` уже есть лог на ту же дату. Привычки сравниваются **по имени**, а не через `is`: при загрузке из БД объекты будут разными, а привычка — той же.

#### `get_logs_for_habit(habit: Habit) -> list[HabitLog]`

Все логи привычки.

#### `get_current_streak(habit: Habit) -> int`

Дней подряд **до сегодня включительно**: идёт от сегодня назад, пока дата есть в `set` отметок. Если сегодня не отмечено — результат `0`.

#### `get_longest_streak(habit: Habit) -> int`

Самая длинная серия за всю историю. Сортировка дат → проход по соседним парам → сброс счётчика при разрыве больше 1 дня → **обязательное** финальное `max` после цикла (иначе теряется серия, заканчивающаяся последним элементом). Пустая история — `0`, один лог — `1`.

#### `get_completion_rate(habit: Habit, days: int = 30) -> float`

Процент выполнения за последние `days` дней (включая сегодня): `фактических / ожидаемых × 100`.

- `EVERYDAY` → ожидается `days` выполнений
- `EVERYWEEK` → ожидаемое число считается точно: сколько дней периода имеют `date.weekday() == habit.weekday`

Если `expected == 0`, возвращается `0.0` (защита от деления на ноль). Результат не ограничен сверху: при лишних отметках может быть больше 100%.

---

## Класс `User`

Владелец набора привычек.

| Поле | Тип | Правило |
|---|---|---|
| `name` | `str` | Не пустое |
| `_habits` | `list[Habit]` | Уникальность по `name` |

#### `add_habit(habit: Habit) -> None`

`DuplicateHabitError`, если привычка с таким названием уже есть.

#### `get_habit_by_name(name: str) -> Habit | None`

Возвращает привычку или `None`. Отсутствие результата — нормальный исход, не ошибка.

---

## Консольный интерфейс

`app/cli.py`, оформление на `rich` (`Console`, `Panel`, `Table`, `Prompt`).

| Пункт | Действие |
|---|---|
| 1. Add habit | Название, описание, периодичность; для `EVERYWEEK` — день недели (ввод 1–7, внутри `-1`) |
| 2. Mark habit | Отметка на сегодня |
| 3. Show statistics | Таблица: статус, день недели, текущая и лучшая серия, completion rate за 30 дней |
| 4. Change habit status | Переключатель archive / activate с подтверждением |
| 5. Exit | Выход |

Ошибки ввода и доменные исключения ловятся (`ValueError`, `IndexError`, `DuplicateHabitError`, `DuplicateLogError`, `HabitArchivedError`), программа не падает. После ошибки ввода — `continue`, чтобы не использовать неопределённые переменные.

> Известный хвост: список дней недели в таблице статистики нужно вынести в константу `WEEKDAYS` рядом с `MENU_TEXT`.

---

## База данных

PostgreSQL 16 поднимается через `docker-compose.yml` (контейнер `habit_tracker_db`, порт `5432`, данные в volume `pgdata`). Доступ — через SQLAlchemy 2 + драйвер `psycopg2`.

### `database.py`

- `engine` — один на всё приложение (внутри пул соединений), создаётся на верхнем уровне
- `Base(DeclarativeBase)` — базовый класс ORM-моделей
- `init_db()` — создаёт таблицы. Импорт `app.db_models` сделан **внутри функции**: он нужен ради регистрации моделей в `Base.metadata`, а на верхнем уровне дал бы циклический импорт

### `db_models.py`: `HabitRecord`

Таблица `habit`:

| Колонка | Тип | Примечание |
|---|---|---|
| `id` | `Integer` | primary key, автоинкремент |
| `name` | `String` | |
| `description` | `String` | |
| `created_at` | `Date` | |
| `weekday` | `Integer` | `NULL` для `EVERYDAY` |
| `status` | `Enum(HabitStatus)` | enum-тип PostgreSQL |
| `frequency` | `Enum(HabitFrequency)` | enum-тип PostgreSQL |

SQLAlchemy хранит **имена** членов Enum (`ACTIVE`), а не значения (`active`). Переименование члена в `enums.py` сломает чтение старых строк.

### Работа с данными

```python
with Session(engine) as session:
    session.add(record)
    session.commit()          # без commit изменения откатываются при выходе из with

with Session(engine) as session:
    stmt = select(HabitRecord).where(HabitRecord.name == "Habit")
    records = session.scalars(stmt).all()   # пустой список [], если ничего нет
```

### Полезные команды

```bash
docker exec -it habit_tracker_db psql -U habit_user -d habit_tracker -c "\dt"
docker exec -it habit_tracker_db psql -U habit_user -d habit_tracker -c "\d habit"
docker exec -it habit_tracker_db psql -U habit_user -d habit_tracker -c "SELECT * FROM habit;"
```

> Ограничение: `create_all` создаёт только отсутствующие таблицы и **не меняет** существующие. Изменения структуры потом будет вести Alembic.

---

## Тесты

```
tests/
├── conftest.py        # общие фикстуры: habit, repo, log, user
├── test_models.py     # Habit
├── test_repository.py # HabitLogRepository
└── test_user.py       # User
```

Запуск: `uv run pytest -v`. Сейчас **17 тестов**:

- `Habit`: пустое имя (параметризованно: `""` и `"   "`), валидные данные, `archive()`, правила `weekday` (4 теста)
- `HabitLogRepository`: добавление, дубликат, current streak (пусто и 3 дня подряд), longest streak (пусто, с разрывом, один лог), completion rate
- `User`: добавление привычки, дубликат

Тесты на БД и на `completion_rate` для `EVERYWEEK` пока не написаны.

### Справочник по pytest

- `assert` — базовая проверка; структура: Arrange → Act → Assert
- `pytest.raises(Тип)` — проверка исключения. Подготовку (первый `add`) выносить **за** `with`, внутрь — только вызов, который должен упасть
- `@pytest.fixture` — переиспользуемые данные; каждый тест получает свежий объект
- `@pytest.mark.parametrize` — один тест на несколько входов
- `conftest.py` — фикстуры доступны во всех файлах папки без импорта
- Имена тестовых функций должны быть уникальными: дубликат имени молча перезаписывает предыдущий тест

---

## Справочник концепций

### `@property` / `@setter`
Метод читается как атрибут (`habit.name`), но с валидацией. Property без setter — только чтение.

### Property vs метод-действие
Property — для значений. Действия, меняющие состояние (`archive()`), — обычные методы со скобками.

### `Enum`
Фиксированный набор значений вместо «голых» строк. Аннотация типа в рантайме не проверяется — для защиты нужен `isinstance` в setter.

### `ValueError` vs `TypeError`
`ValueError` — подходящий тип, но неверное значение. `TypeError` — неподходящий тип.

### Сравнение по полю, а не по `is`
`is` сравнивает идентичность в памяти и ненадёжен, если объекты загружаются заново (БД). Сравнение по `name` от этого не зависит.

### Циклические зависимости
`Habit` не хранит ссылку на `User` (принцип единственной ответственности). Тот же принцип: `database.py` не импортирует `db_models` на верхнем уровне.

### Импорты и запуск как модуля
`uv run app/main.py` добавляет в `sys.path` папку `app/`, и `from app.models import ...` не находит пакет. `uv run -m app.main` ищет от корня проекта.

### `set` vs `list` для `in`
`in` для `list` — O(n), для `set` — в среднем O(1) за счёт хеширования.

### `try` / `except`
Ловить конкретные типы (`except ValueError`), не голый `except:`. После обработки ошибки в цикле — `continue`, если дальше нужны переменные, которые не создались.

### Implicit string concatenation
Строковые литералы подряд склеиваются без разделителя: `\n` нужно ставить вручную.

### DRY
Повторяющийся код выносится в функцию или переменную (`find_habit()`, общие фикстуры в `conftest.py`).

### Слоистая архитектура и репозиторий
Домен (бизнес-логика) отдельно от хранения (ORM). Репозиторий скрывает, где и как лежат данные.

### ORM, Session, commit
ORM отображает таблицы на классы. `Session` — «рабочая область»: `add()` кладёт объект в сессию, `commit()` отправляет изменения в БД, выход из `with` без `commit()` откатывает их.

### `Base.metadata`
Реестр таблиц. Модель попадает туда, когда выполняется её `class`. `create_all` строит таблицы только по тому, что уже зарегистрировано; пустой реестр — тихое «ничего не создано».

---

## Roadmap

- [x] Доменная модель: `Habit`, `HabitLog`, `HabitLogRepository`, `User`
- [x] Статистика: streak и completion rate
- [x] Консольный интерфейс на `rich`
- [x] Тесты (pytest), 17 шт.
- [x] `weekday` для `EVERYWEEK` и точный completion rate
- [ ] База данных
  - [x] PostgreSQL в Docker
  - [x] SQLAlchemy: `engine`, `Base`, `init_db()`
  - [x] `HabitRecord` со всеми полями, вставка и чтение через `Session`
  - [ ] Перевод `HabitRecord` ↔ `Habit` (где живёт — открытый вопрос)
  - [ ] Остальные таблицы: пользователи, логи
  - [ ] Репозиторий поверх БД
  - [ ] Пароль и настройки в `.env`
  - [ ] Alembic
- [ ] REST API (FastAPI, авторизация, слоистая архитектура)
- [ ] Фронтенд (после готового API)