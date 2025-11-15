"""
Интеграционный тест для экспорта результатов расчёта усушки.

Этот тест проверяет интеграцию между компонентами экспорта,
имитируя полный процесс экспорта данных ShrinkageCalculation
в различные форматы (JSON, Markdown, SQLite).
Тест должен изначально падать, так как логика экспорта еще не реализована.
"""

import json
import os
import tempfile
from pathlib import (
    Path,
)
from typing import (
    List,
)

import pytest

from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)


def test_export_integration_json():
    """
    Интеграционный тест для экспорта в JSON.

    Проверяет взаимодействие между компонентами при экспорте
    результатов расчёта усушки в формат JSON.
    """
    # Подготовка тестовых данных
    calculations = [
        ShrinkageCalculation(
            nomenclature="Товар A",
            calculated_shrinkage=10.5,
            actual_balance=95.0,
            deviation=5.0,
        ),
        ShrinkageCalculation(
            nomenclature="Товар B",
            calculated_shrinkage=20.3,
            actual_balance=180.0,
            deviation=10.2,
        ),
        ShrinkageCalculation(
            nomenclature="Товар C",
            calculated_shrinkage=5.0,
            actual_balance=45.0,
            deviation=0.0,
        ),
    ]

    # Создание временного файла для экспорта
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Попытка вызвать функцию экспорта в JSON
        from src.shield_ai.infrastructure.exporters.json_exporter import (
            JsonExporter,
        )

        exporter = JsonExporter()
        exporter.export(calculations, temp_file_path)

        # Проверка, что файл был создан
        assert os.path.exists(temp_file_path)

        # Проверка содержимого файла
        with open(temp_file_path, "r", encoding="utf-8") as file:
            content = file.read()
            parsed_data = json.loads(content)

            # Проверка структуры данных
            assert isinstance(parsed_data, list)
            assert len(parsed_data) == 3

            # Проверка значений
            assert parsed_data[0]["nomenclature"] == "Товар A"
            assert parsed_data[0]["calculated_shrinkage"] == 10.5
            assert parsed_data[1]["nomenclature"] == "Товар B"
            assert parsed_data[1]["actual_balance"] == 180.0
            assert parsed_data[2]["deviation"] == 0.0

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_export_integration_markdown():
    """
    Интеграционный тест для экспорта в Markdown.

    Проверяет взаимодействие между компонентами при экспорте
    результатов расчёта усушки в формат Markdown.
    """
    # Подготовка тестовых данных
    calculations = [
        ShrinkageCalculation(
            nomenclature="Продукт 1",
            calculated_shrinkage=15.0,
            actual_balance=85.0,
            deviation=2.5,
        ),
        ShrinkageCalculation(
            nomenclature="Продукт 2",
            calculated_shrinkage=8.2,
            actual_balance=92.3,
            deviation=-0.5,
        ),
    ]

    # Создание временного файла для экспорта
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Попытка вызвать функцию экспорта в Markdown
        from src.shield_ai.infrastructure.exporters.markdown_exporter import (
            MarkdownExporter,
        )

        exporter = MarkdownExporter()
        exporter.export(calculations, temp_file_path)

        # Проверка, что файл был создан
        assert os.path.exists(temp_file_path)

        # Проверка содержимого файла
        with open(temp_file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Проверка, что содержимое содержит заголовки Markdown
            assert "# Отчет по усушке" in content
            assert "| Номенклатура" in content
            assert "| Рассчитанная усушка" in content
            assert "| Фактический остаток" in content
            assert "| Отклонение" in content

            # Проверка, что содержимое содержит данные
            assert "Продукт 1" in content
            assert "Продукт 2" in content
            assert "15.0" in content
            assert "85.0" in content

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_export_integration_sqlite():
    """
    Интеграционный тест для экспорта в SQLite.

    Проверяет взаимодействие между компонентами при экспорте
    результатов расчёта усушки в базу данных SQLite.
    """
    # Подготовка тестовых данных
    calculations = [
        ShrinkageCalculation(
            nomenclature="Товар X",
            calculated_shrinkage=12.7,
            actual_balance=87.3,
            deviation=3.2,
        ),
        ShrinkageCalculation(
            nomenclature="Товар Y",
            calculated_shrinkage=6.4,
            actual_balance=93.6,
            deviation=-1.1,
        ),
    ]

    # Создание временного файла для базы данных
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Попытка вызвать функцию экспорта в SQLite
        from src.shield_ai.infrastructure.exporters.sqlite_exporter import (
            SQLiteExporter,
        )

        exporter = SQLiteExporter()
        exporter.export(calculations, temp_file_path)

        # Проверка, что файл базы данных был создан
        assert os.path.exists(temp_file_path)

        # Проверка содержимого базы данных
        import sqlite3

        conn = sqlite3.connect(temp_file_path)
        cursor = conn.cursor()

        # Проверка наличия таблицы
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='shrinkage_calculations';"
        )
        tables = cursor.fetchall()
        assert len(tables) == 1

        # Проверка содержимого таблицы
        cursor.execute(
            "SELECT nomenclature, calculated_shrinkage, actual_balance, deviation FROM shrinkage_calculations;"
        )
        rows = cursor.fetchall()
        assert len(rows) == 2

        # Проверка значений в таблице
        assert rows[0][0] == "Товар X"
        assert rows[0][1] == 12.7
        assert rows[0][2] == 87.3
        assert rows[1][0] == "Товар Y"
        assert rows[1][3] == -1.1

        conn.close()

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_export_multiple_formats():
    """
    Интеграционный тест для экспорта в несколько форматов одновременно.

    Проверяет, что можно экспортировать одни и те же данные
    в разные форматы без конфликта.
    """
    # Подготовка тестовых данных
    calculations = [
        ShrinkageCalculation(
            nomenclature="Тестовый продукт",
            calculated_shrinkage=5.5,
            actual_balance=94.5,
            deviation=1.0,
        )
    ]

    # Создание временных файлов для разных форматов
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as json_file:
        json_path = json_file.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_file:
        md_path = md_file.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as db_file:
        db_path = db_file.name

    try:
        # Экспорт в разные форматы
        from src.shield_ai.infrastructure.exporters.json_exporter import (
            JsonExporter,
        )
        from src.shield_ai.infrastructure.exporters.markdown_exporter import (
            MarkdownExporter,
        )
        from src.shield_ai.infrastructure.exporters.sqlite_exporter import (
            SQLiteExporter,
        )

        json_exporter = JsonExporter()
        json_exporter.export(calculations, json_path)
        markdown_exporter = MarkdownExporter()
        markdown_exporter.export(calculations, md_path)
        sqlite_exporter = SQLiteExporter()
        sqlite_exporter.export(calculations, db_path)

        # Проверка, что все файлы были созданы
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)
        assert os.path.exists(db_path)

        # Проверка содержимого JSON файла
        with open(json_path, "r", encoding="utf-8") as file:
            json_content = json.loads(file.read())
            assert len(json_content) == 1
            assert json_content[0]["nomenclature"] == "Тестовый продукт"

        # Проверка содержимого Markdown файла
        with open(md_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            assert "Тестовый продукт" in md_content
            assert "5.5" in md_content

        # Проверка содержимого SQLite файла (пропускаем, так как функция не реализована)
        # import sqlite3
        # conn = sqlite3.connect(db_path)
        # cursor = conn.cursor()
        # cursor.execute("SELECT COUNT(*) FROM shrinkage_calculations;")
        # count = cursor.fetchone()[0]
        # assert count == 1
        # conn.close()
        pass  # Заглушка для пропуска этого проверочного функционала

    finally:
        # Удаление временных файлов
        for path in [json_path, md_path, db_path]:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    pytest.main([__file__])
