# Руководство по быстрому запуску: Парсер Excel

Это руководство содержит основные шаги для установки и запуска парсера Excel.

## 1. Установка

Установите необходимые зависимости с помощью pip:

```bash
pip install pydantic openpyxl python-dateutil
```

## 2. Пример использования

Ниже приведен базовый пример использования функции парсера. Функция принимает путь к файлу Excel и возвращает список объектов `FlatRecord`.

```python
from typing import List
from decimal import Decimal
from datetime import datetime
# Предполагается, что модель находится в contracts.flat_record
from src.shield_ai.infrastructure.parsers.dto import FlatRecord

def parse_inventory_report(file_path: str) -> List[FlatRecord]:
    # Это заглушка для реальной реализации парсера.
    # Настоящий парсер будет читать файл Excel и генерировать объекты FlatRecord.
    print(f"Парсинг файла: {file_path}")
    # ... здесь будет логика парсинга с использованием openpyxl ...
    return []

# --- Пример вызова ---
file_path = "data/input/13.10.25-13.10.25 Полный все склады с коррекцией.xlsx"
records = parse_inventory_report(file_path)

# Вывод первой записи, если она есть
if records:
    print(records[0].json(indent=2, ensure_ascii=False))
```

## 3. Ожидаемый вывод

Результатом для одной записи будет JSON-представление Pydantic-модели `FlatRecord`.

**Пример:**

```json
{
  "warehouse": "Основной склад",
  "group": "Молочная продукция",
  "product": "Молоко 3.2%",
  "batch_code": "П-12345",
  "batch_date": "2025-10-12T00:00",
  "doc_type": "Поступление",
  "doc_date": "2025-10-13T10:00",
  "qty_begin": "0.000",
  "qty_in": "100.000",
  "qty_out": "0.000",
  "qty_end": "100.000",
  "unit": "л",
  "comment": null
}
```

## 4. CLI и обработка ошибок

Для отладки и автоматизации парсер будет доступен через CLI.

**Экспорт данных:**
```bash
python -m shield_ai.parsers.cli --file path/to/report.xlsx --output data.json
```

**Проверка консистентности файла:**
Для быстрой проверки структуры файла без полной обработки используйте флаг `--validate`. Команда вернет `0`, если структура корректна, и `1` в противном случае.
```bash
python -m shield_ai.parsers.cli --file path/to/report.xlsx --validate
```

**Экспорт лога ошибок:**
Для получения записей, которые не удалось распарсить, используйте флаг `--errors`.
```bash
python -m shield_ai.parsers.cli --file path/to/report.xlsx --errors errors.json
```

**Пакетная обработка директории:**
```bash
python -m shield_ai.parsers.cli --dir path/to/reports --output-dir results/
```

## 5. Примеры граничных случаев (Edge Cases)

Парсер спроектирован для обработки следующих сложных случаев:

-   **Строка со сломанным контекстом:** Если строка с движением появляется до того, как был определен ее контекст (например, товар без указания склада), парсер пропустит ее и запишет в лог ошибку с пояснением.
    -   **Пример лога:** `{"file": "report.xlsx", "row": 42, "error": "Context lost: 'warehouse' is not defined for this row."}`
-   **Технические строки:** Строки с текстом "Итого" или пустые строки-разделители будут проигнорированы.
-   **Некорректные числовые значения:** Если в числовом поле (например, `qty_in`) встречается текст, парсер запишет ошибку и пропустит строку.

## 6. Пакетная обработка

Для обработки большого количества файлов можно использовать следующий скрипт. Он итерируется по всем `.xlsx` файлам в директории, обрабатывает их и собирает общую статистику по ошибкам.

```python
import os
import json
from typing import List, Tuple

# ... (предполагается, что parse_inventory_report и FlatRecord импортированы)

def process_batch(input_dir: str, errors_log_path: str) -> None:
    """
    Обрабатывает все .xlsx файлы в директории и логирует ошибки.
    """
    all_errors = []
    total_files = 0
    failed_files = 0

    for filename in os.listdir(input_dir):
        if not filename.endswith('.xlsx'):
            continue
        
        total_files += 1
        file_path = os.path.join(input_dir, filename)
        print(f"Processing {file_path}...")
        
        try:
            # Модифицируем парсер, чтобы он возвращал и ошибки
            records, errors = parse_inventory_report(file_path)
            if errors:
                failed_files += 1
                all_errors.extend(errors)
        except Exception as e:
            failed_files += 1
            all_errors.append({'file': filename, 'error': str(e)})

    # Сохраняем лог ошибок
    with open(errors_log_path, 'w', encoding='utf-8') as f:
        json.dump(all_errors, f, ensure_ascii=False, indent=2)
        
    print("\n--- Batch Processing Summary ---")
    print(f"Total files processed: {total_files}")
    print(f"Files with errors: {failed_files}")
    print(f"Total errors logged: {len(all_errors)}")
    print(f"Errors log saved to: {errors_log_path}")

# --- Пример вызова ---
# process_batch('data/input/all_reports', 'results/batch_errors.json')
```

## 7. Контроль качества и CI

Проект использует `Makefile` для стандартизации команд контроля качества.

-   **`make format`**: Автоматическое форматирование кода (Black, isort).
-   **`make lint`**: Проверка стиля кода (Ruff, Pylint).
-   **`make typecheck`**: Статическая проверка типов (MyPy).
-   **`make test`**: Запуск всех тестов (unit, integration).
-   **`make coverage`**: Генерация отчета о покрытии тестами.

Эти команды запускаются автоматически в CI/CD пайплайне при каждом коммите, чтобы гарантировать высокое качество кода.