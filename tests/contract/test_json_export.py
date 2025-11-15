"""
Контрактный тест для экспорта в JSON.

Этот тест проверяет контракт функции экспорта результатов расчётов в JSON формат,
имитируя входные данные и проверяя ожидаемое поведение.
Тест должен изначально падать, так как логика экспорта еще не реализована.
"""

import json
from typing import (
    List,
)

import pytest

from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)


def test_json_export_contract():
    """
    Тестирует контракт функции экспорта результатов расчёта усушки в JSON формат.

    Сценарий:
    - Имеется список результатов расчёта усушки (ShrinkageCalculation)
    - Вызывается функция экспорта в JSON
    - Ожидается, что функция вернет корректную JSON-строку с результатами
    """
    # Подготовка данных для теста
    shrinkage_calculations = [
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

    # Попытка вызвать функцию экспорта в JSON
    import json
    import os
    import tempfile

    from src.shield_ai.infrastructure.exporters.json_exporter import (
        JsonExporter,
    )

    # Создание временного файла для экспорта
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Создание экземпляра JsonExporter и вызов метода экспорта
        exporter = JsonExporter()
        exporter.export(shrinkage_calculations, temp_file_path)

        # Чтение содержимого файла для проверки
        with open(temp_file_path, "r", encoding="utf-8") as file:
            json_result = file.read()

        # Проверка, что результат является строкой
        assert isinstance(json_result, str)

        # Проверка, что результат может быть десериализован как JSON
        parsed_json = json.loads(json_result)

        # Проверка структуры JSON
        assert isinstance(parsed_json, list)
        assert len(parsed_json) == 3

        # Проверка, что каждый элемент списка содержит ожидаемые поля
        for item in parsed_json:
            assert "nomenclature" in item
            assert "calculated_shrinkage" in item
            assert "actual_balance" in item
            assert "deviation" in item

        # Проверка значений в JSON
        assert parsed_json[0]["nomenclature"] == "Товар A"
        assert parsed_json[0]["calculated_shrinkage"] == 10.5
        assert parsed_json[0]["actual_balance"] == 95.0
        assert parsed_json[0]["deviation"] == 5.0

        assert parsed_json[1]["nomenclature"] == "Товар B"
        assert parsed_json[1]["calculated_shrinkage"] == 20.3
        assert parsed_json[1]["actual_balance"] == 180.0
        assert parsed_json[1]["deviation"] == 10.2

        assert parsed_json[2]["nomenclature"] == "Товар C"
        assert parsed_json[2]["calculated_shrinkage"] == 5.0
        assert parsed_json[2]["actual_balance"] == 45.0
        assert parsed_json[2]["deviation"] == 0.0

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Проверка, что результат является строкой
    assert isinstance(json_result, str)

    # Проверка, что результат может быть десериализован как JSON
    parsed_json = json.loads(json_result)

    # Проверка структуры JSON
    assert isinstance(parsed_json, list)
    assert len(parsed_json) == 3

    # Проверка, что каждый элемент списка содержит ожидаемые поля
    for item in parsed_json:
        assert "nomenclature" in item
        assert "calculated_shrinkage" in item
        assert "actual_balance" in item
        assert "deviation" in item

    # Проверка значений в JSON
    assert parsed_json[0]["nomenclature"] == "Товар A"
    assert parsed_json[0]["calculated_shrinkage"] == 10.5
    assert parsed_json[0]["actual_balance"] == 95.0
    assert parsed_json[0]["deviation"] == 5.0

    assert parsed_json[1]["nomenclature"] == "Товар B"
    assert parsed_json[1]["calculated_shrinkage"] == 20.3
    assert parsed_json[1]["actual_balance"] == 180.0
    assert parsed_json[1]["deviation"] == 10.2

    assert parsed_json[2]["nomenclature"] == "Товар C"
    assert parsed_json[2]["calculated_shrinkage"] == 5.0
    assert parsed_json[2]["actual_balance"] == 45.0
    assert parsed_json[2]["deviation"] == 0.0


def test_json_export_empty_list_contract():
    """
    Тестирует контракт функции экспорта в JSON с пустым списком.

    Сценарий:
    - Имеется пустой список результатов расчёта усушки
    - Вызывается функция экспорта в JSON
    - Ожидается, что функция вернет пустой JSON-массив
    """
    # Подготовка пустого списка
    empty_calculations: List[ShrinkageCalculation] = []

    # Попытка вызвать функцию экспорта в JSON
    import json
    import os
    import tempfile

    from src.shield_ai.infrastructure.exporters.json_exporter import (
        JsonExporter,
    )

    # Создание временного файла для экспорта
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Создание экземпляра JsonExporter и вызов метода экспорта
        exporter = JsonExporter()
        exporter.export(empty_calculations, temp_file_path)

        # Чтение содержимого файла для проверки
        with open(temp_file_path, "r", encoding="utf-8") as file:
            json_result = file.read()

        # Проверка, что результат является строкой
        assert isinstance(json_result, str)

        # Проверка, что результат может быть десериализован как JSON
        parsed_json = json.loads(json_result)

        # Проверка, что результат - пустой массив
        assert isinstance(parsed_json, list)
        assert len(parsed_json) == 0

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Проверка, что результат является строкой
    assert isinstance(json_result, str)

    # Проверка, что результат может быть десериализован как JSON
    parsed_json = json.loads(json_result)

    # Проверка, что результат - пустой массив
    assert isinstance(parsed_json, list)
    assert len(parsed_json) == 0


def test_json_export_single_item_contract():
    """
    Тестирует контракт функции экспорта в JSON с одним элементом.

    Сценарий:
    - Имеется список с одним результатом расчёта усушки
    - Вызывается функция экспорта в JSON
    - Ожидается, что функция вернет корректный JSON-массив с одним элементом
    """
    # Подготовка данных с одним элементом
    single_calculation = [
        ShrinkageCalculation(
            nomenclature="Товар X",
            calculated_shrinkage=15.7,
            actual_balance=85.5,
            deviation=2.3,
        )
    ]

    # Попытка вызвать функцию экспорта в JSON
    import json
    import os
    import tempfile

    from src.shield_ai.infrastructure.exporters.json_exporter import (
        JsonExporter,
    )

    # Создание временного файла для экспорта
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name

    try:
        # Создание экземпляра JsonExporter и вызов метода экспорта
        exporter = JsonExporter()
        exporter.export(single_calculation, temp_file_path)

        # Чтение содержимого файла для проверки
        with open(temp_file_path, "r", encoding="utf-8") as file:
            json_result = file.read()

        # Проверка, что результат является строкой
        assert isinstance(json_result, str)

        # Проверка, что результат может быть десериализован как JSON
        parsed_json = json.loads(json_result)

        # Проверка структуры JSON
        assert isinstance(parsed_json, list)
        assert len(parsed_json) == 1

        # Проверка, что элемент содержит ожидаемые поля
        item = parsed_json[0]
        assert "nomenclature" in item
        assert "calculated_shrinkage" in item
        assert "actual_balance" in item
        assert "deviation" in item

        # Проверка значений в JSON
        assert item["nomenclature"] == "Товар X"
        assert item["calculated_shrinkage"] == 15.7
        assert item["actual_balance"] == 85.5
        assert item["deviation"] == 2.3

    finally:
        # Удаление временного файла
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Проверка, что результат является строкой
    assert isinstance(json_result, str)

    # Проверка, что результат может быть десериализован как JSON
    parsed_json = json.loads(json_result)

    # Проверка структуры JSON
    assert isinstance(parsed_json, list)
    assert len(parsed_json) == 1

    # Проверка, что элемент содержит ожидаемые поля
    item = parsed_json[0]
    assert "nomenclature" in item
    assert "calculated_shrinkage" in item
    assert "actual_balance" in item
    assert "deviation" in item

    # Проверка значений в JSON
    assert item["nomenclature"] == "Товар X"
    assert item["calculated_shrinkage"] == 15.7
    assert item["actual_balance"] == 85.5
    assert item["deviation"] == 2.3


if __name__ == "__main__":
    pytest.main([__file__])
