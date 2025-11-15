# 📤 Shield AI v2.0 - Экспортеры данных

## 1. Введение

Модуль экспортеров в Shield AI предоставляет унифицированный интерфейс для сохранения обработанных данных в различных форматах. Это позволяет гибко интегрировать результаты работы системы с другими инструментами и системами.

Все экспортеры реализуют интерфейс `Exporter` (`src/shield_ai/infrastructure/export_interfaces.py`), обеспечивая полиморфное поведение.

## 2. Обзор экспортеров

### 2.1. `JsonExporter` - Экспорт в JSON

**Файл**: [`src/shield_ai/infrastructure/exporters/json_exporter.py`](src/shield_ai/infrastructure/exporters/json_exporter.py)

**Назначение**: Экспортирует список объектов `ShrinkageCalculation` в JSON-файл.

**Принцип работы**:
`JsonExporter` преобразует список объектов `ShrinkageCalculation` в список словарей, а затем сериализует его в JSON-формат. Используется кастомный `JsonEncoder` для корректной обработки специфических типов данных, таких как `datetime.date`.

**Методы**:
*   `export(data: List[ShrinkageCalculation], output_path: str) -> None`: Основной метод для выполнения экспорта. Принимает список `ShrinkageCalculation` и путь к выходному файлу.

**Пример использования (псевдокод)**:
```python
exporter = JsonExporter()
exporter.export(list_of_shrinkage_calculations, "results/shrinkage_report.json")
```

### 2.2. `MarkdownExporter` - Экспорт в Markdown

**Файл**: [`src/shield_ai/infrastructure/exporters/markdown_exporter.py`](src/shield_ai/infrastructure/exporters/markdown_exporter.py)

**Назначение**: Экспортирует список объектов `ShrinkageCalculation` в Markdown-файл.

**Принцип работы**:
`MarkdownExporter` генерирует отчет в формате Markdown, включая заголовок, таблицу с результатами расчета усушки и дополнительную информацию.

**Методы**:
*   `export(data: List[ShrinkageCalculation], output_path: str) -> None`: Основной метод для выполнения экспорта. Принимает список `ShrinkageCalculation` и путь к выходному файлу.

**Пример использования (псевдокод)**:
```python
exporter = MarkdownExporter()
exporter.export(list_of_shrinkage_calculations, "results/shrinkage_report.md")
```

### 2.3. `SQLiteExporter` - Экспорт в SQLite

**Файл**: [`src/shield_ai/infrastructure/exporters/sqlite_exporter.py`](src/shield_ai/infrastructure/exporters/sqlite_exporter.py)

**Назначение**: Экспортирует список объектов `ShrinkageCalculation` в SQLite базу данных.

**Принцип работы**:
`SQLiteExporter` использует SQLAlchemy ORM для создания таблицы `shrinkage_calculations` в указанной SQLite базе данных и записывает в нее результаты расчета усушки. Перед вставкой новых данных таблица очищается.

**Методы**:
*   `export(data: List[ShrinkageCalculation], output_path: str) -> None`: Основной метод для выполнения экспорта. Принимает список `ShrinkageCalculation` и путь к файлу базы данных SQLite.

**ORM Модель**:
*   `ShrinkageCalculationORM`: ORM модель, представляющая таблицу `shrinkage_calculations` со следующими полями:
    *   `id` (Integer, Primary Key)
    *   `nomenclature` (String)
    *   `calculated_shrinkage` (Float)
    *   `actual_balance` (Float)
    *   `deviation` (Float)

**Пример использования (псевдокод)**:
```python
exporter = SQLiteExporter()
exporter.export(list_of_shrinkage_calculations, "data/database/shrinkage.db")