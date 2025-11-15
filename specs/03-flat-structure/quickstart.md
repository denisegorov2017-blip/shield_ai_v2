# Quick Start: Рефакторинг проекта для расчёта усушки и учёта по партиям

**Ветка**: `03-flat-structure` | **Дата**: 2025-11-14 | **Спецификация**: [specs/03-flat-structure/spec.md](specs/03-flat-structure/spec.md:1)

## Обзор

Quick Start руководство для разработчиков, присоединяющихся к проекту по рефакторингу shield_ai_v2 с целью упрощения расчёта усушки и учёта по партиям. В этом руководстве описаны основные шаги для настройки среды разработки и начала работы с новой flat-архитектурой.

## Подготовка среды разработки

### Требования

- Python 3.12
- pip
- virtualenv (рекомендуется)

### Установка

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd shield_ai_v2
   ```

2. **Создание виртуального окружения**
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. **Установка зависимостей**
   ```bash
   pip install -r requirements.txt
   ```

4. **Установка pre-commit hooks (опционально, но рекомендуется)**
   ```bash
   pre-commit install
   ```

## Структура проекта

```
shield_ai_v2/
├── src/
│   └── shield_ai/
│       ├── domain/           # Бизнес-логика и сущности
│       │   ├── entities/     # Dataclasses: BatchMovement, BatchBalance, ShrinkageCalculation
│       │   └── shrinkage/    # Стратегии расчёта усушки
│       ├── application/      # Use cases
│       │   └── use_cases/    # Бизнес-процессы
│       ├── infrastructure/   # Внешние зависимости
│       │   ├── parsers/      # Парсеры Excel/JSON/MD
│       │   └── database/     # Модели и сессии БД
│       └── presentation/     # UI слой
│           └── ui/           # Streamlit страницы
├── tests/                    # Тесты
├── data/                     # Примеры данных
├── specs/03-flat-structure/  # Текущая спецификация
└── pages/                    # Streamlit страницы (устаревшие, для совместимости)
```

## Основные сущности

### BatchMovement
```python
from datetime import date

# Представляет движение товара по партии
movement = BatchMovement(
    nomenclature="Пиво светлое",
    date=date(2025, 1, 15),
    movement_type="Приход",
    quantity=1000.0,
    warehouse="Склад №1"
)
```

### BatchBalance
```python
# Представляет остаток товара по партии
balance = BatchBalance(
    nomenclature="Пиво светлое",
    date=date(2025, 1, 31),
    balance=850.0,
    warehouse="Склад №1",
    batch="B20250101001"
)
```

### ShrinkageCalculation
```python
# Результат расчёта усушки
calculation = ShrinkageCalculation(
    product_name="Пиво светлое",
    calculation_period_start=date(2025, 1, 1),
    calculation_period_end=date(2025, 1, 31),
    initial_balance=1000.0,
    movements_total=-150.0,
    final_balance=850.0,
    calculated_shrinkage=5.0,  # Нормативная усушка
    actual_shrinkage=0.0,      # Фактическая убыль
    shrinkage_percentage=0.5,
    variance=-5.0              # Отклонение (факт - норма)
)
```

## Основные процессы

### 1. Импорт данных

```python
from src.shield_ai.infrastructure.parsers.inventory_parser import parse_inventory_file

# Загрузка Excel файла и преобразование в flat таблицу
dataframe = parse_inventory_file("path/to/inventory.xlsx")

# Преобразование в список BatchMovement
# Убедитесь, что DataFrame содержит правильные колонки: номенклатура, дата, тип_движения, количество, склад
movements = [
    BatchMovement(
        nomenclature=row['Номенклатура'],
        date=row['Дата'],
        movement_type=row['ТипДвижения'],
        quantity=row['Количество'],
        warehouse=row['Склад']
    )
    for row in dataframe.to_dict('records')
]
```

### 2. Расчёт усушки

```python
from src.shield_ai.application.use_cases.forecast_shrinkage import calculate_shrinkage

# Вычисление усушки по списку движений
calculations = calculate_shrinkage(movements, start_date, end_date)
```

### 3. Экспорт результатов

```python
# Экспорт в JSON
calculations_json = [calc.__dict__ for calc in calculations]
with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(calculations_json, f, ensure_ascii=False, default=str)

# Экспорт в Markdown
with open('results.md', 'w', encoding='utf-8') as f:
    f.write("# Результаты расчёта усушки\n")
    for calc in calculations:
        f.write(f"## {calc.product_name}\n")
        f.write(f"- Начальный остаток: {calc.initial_balance}\n")
        f.write(f"- Усушка по норме: {calc.calculated_shrinkage}\n")
        f.write(f"- Фактическая убыль: {calc.actual_shrinkage}\n")
        f.write(f"- Отклонение: {calc.variance}\n")
```

## Тестирование

### Запуск юнит-тестов

```bash
# Все тесты
pytest

# Тесты для конкретного модуля
pytest tests/unit/domain/

# С покрытием
pytest --cov=src/shield_ai --cov-report=html
```

### Запуск интеграционных тестов

```bash
pytest tests/integration/
```

## Запуск UI

```bash
# Запуск Streamlit приложения
streamlit run src/shield_ai/presentation/ui/main.py

# Или запуск конкретной страницы
streamlit run src/shield_ai/presentation/ui/pages/1_parse.py
```

## Основные изменения в архитектуре

### До рефакторинга:
- Сложная логика FIFO и пересортицы в основном импорте
- Глубокие классовые иерархии
- Сложные связи между сущностями

### После рефакторинга:
- Flat-преобразование отчёта (один лист → плоская таблица)
- Простые dataclasses для представления данных
- Чёткое разделение на слои: domain, application, infrastructure, presentation
- Упрощённая логика расчёта усушки

## Настройка и конфигурация

### Конфигурационные файлы

- `.env` - для настройки переменных окружения
- `pyproject.toml` - для настройки инструментов (pytest, mypy, black, и т.д.)

### Пример .env файла

```
# Пути к данным
INPUT_DATA_PATH=data/input/
OUTPUT_DATA_PATH=data/output/

# Настройки БД
DATABASE_URL=sqlite:///./shield_ai.db

# Параметры расчёта усушки
DEFAULT_SHELF_LIFE_DAYS=30
DEFAULT_SHRINKAGE_RATE=0.5
```

## Наиболее важные файлы

1. **[src/shield_ai/domain/entities/batch.py](src/shield_ai/domain/entities/batch.py:1)** - Определение основных сущностей
2. **[src/shield_ai/infrastructure/parsers/inventory_parser.py](src/shield_ai/infrastructure/parsers/inventory_parser.py:1)** - Парсер Excel файлов
3. **[src/shield_ai/application/use_cases/forecast_shrinkage.py](src/shield_ai/application/use_cases/forecast_shrinkage.py:1)** - Логика расчёта усушки
4. **[src/shield_ai/presentation/ui/pages/1_parse.py](src/shield_ai/presentation/ui/pages/1_parse.py:1)** - UI для импорта данных

## Типичные задачи

### Добавление нового типа движения

1. Обновить enum или тип данных для `movement_type` в `BatchMovement`
2. Добавить обработку в парсере
3. Покрыть тестами

### Изменение логики расчёта усушки

1. Обновить стратегию в `src/shield_ai/domain/shrinkage/strategies.py`
2. Обновить соответствующие use cases
3. Обновить тесты

## Отладка

### Включение логирования

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Типичные проблемы и решения

- **Проблема**: Медленная обработка больших Excel файлов
  - **Решение**: Использовать chunking при чтении или оптимизировать pandas операции

- **Проблема**: Неверные расчёты усушки
  - **Решение**: Проверить типы данных и форматы дат в исходных данных

- **Проблема**: Проблемы с типизацией
  - **Решение**: Запустить mypy для проверки: `mypy src/`

## Следующие шаги

1. Ознакомьтесь с полной спецификацией: [specs/03-flat-structure/spec.md](specs/03-flat-structure/spec.md:1)
2. Проверьте план реализации: [specs/03-flat-structure/plan.md](specs/03-flat-structure/plan.md:1)
3. Запустите тесты, чтобы убедиться, что среда настроена правильно
4. Попробуйте запустить UI и выполнить базовый сценарий импорта данных