"""
Интеграционный тест для расчёта усушки по упрощённой логике (Пользовательская история 2)

Тест проверяет взаимодействие между компонентами:
- стратегией расчёта усушки
- use case для прогноза усушки
- dataclass ShrinkageCalculation

Этот тест должен изначально падать, поскольку логика расчёта усушки и use case ещё не реализованы.
"""

from datetime import (
    datetime,
)
from typing import (
    Any,
    Dict,
)

import pytest

from src.shield_ai.application.use_cases.forecast_shrinkage import (
    ForecastShrinkageUseCase,
)
from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)
from src.shield_ai.domain.shrinkage.strategies import (
    CompatibilityStrategy,
)


def test_shrinkage_calculation_integration():
    """
    Интеграционный тест: проверяет взаимодействие между стратегией расчёта усушки
    и use case, возвращающим результат в формате ShrinkageCalculation.

    Пользовательская история 2 - Расчёт усушки по упрощённой логике
    Сценарий: Даны плоские данные по остаткам и движениям,
    Когда пользователь запускает расчёт усушки,
    Тогда система возвращает отчёт с расчётами усушки по номенклатуре
    """
    # Подготовка тестовых данных
    nomenclature = "Пиво светлое 0.5л"
    initial_balance = 1000.0  # начальный остаток
    final_balance = 950.0  # фактический конечный остаток
    movement_total = 50.0  # всего движений
    days_stored = 30  # дней хранения

    # Подготовка данных для стратегии расчёта
    batch_data = {"initial_mass": initial_balance, "days_stored": days_stored}

    # Коэфициенты для расчёта усушки
    coeffs = {
        "a": 0.001,  # начальная скорость усушки
        "b": 0.05,  # скорость затухания усушки
        "c": 0.0001,  # базовый уровень усушки
    }

    # Используем стратегию расчёта усушки
    strategy = CompatibilityStrategy()

    # Выполняем расчёт усушки с помощью стратегии
    calculated_shrinkage = strategy.calculate(batch_data, coeffs)

    # Рассчитываем отклонение (разница между ожидаемым и фактическим остатком)
    expected_final_balance = initial_balance - movement_total - calculated_shrinkage
    deviation = final_balance - expected_final_balance

    # Создаём результат в формате ShrinkageCalculation
    result = ShrinkageCalculation(
        nomenclature=nomenclature,
        calculated_shrinkage=calculated_shrinkage,
        actual_balance=final_balance,
        deviation=deviation,
    )

    # Проверки
    assert isinstance(result, ShrinkageCalculation)
    assert result.nomenclature == nomenclature
    assert isinstance(result.calculated_shrinkage, (int, float))
    assert result.actual_balance == final_balance
    assert isinstance(result.deviation, (int, float))

    # Проверяем, что результаты логичны
    assert result.calculated_shrinkage >= 0  # усушка не может быть отрицательной
    assert result.actual_balance >= 0  # остаток не может быть отрицательным


def test_forecast_shrinkage_use_case_integration():
    """
    Интеграционный тест: проверяет работу use case ForecastShrinkage
    с реальной базой данных (через сессию).

    Этот тест должен изначально падать, так как use case и его зависимости
    ещё не полностью реализованы для возврата ShrinkageCalculation.
    """
    # Этот тест должен изначально падать, так как ожидаемая функциональность
    # ещё не реализована. В TDD тесты пишутся до реализации.

    # Выбрасываем исключение, чтобы тест был помечен как падающий
    # Это сигнализирует, что требуемая функциональность ещё не реализована
    raise NotImplementedError(
        "Функциональность ForecastShrinkageUseCase для возврата ShrinkageCalculation "
        "ещё не реализована. Это ожидаемое поведение до тех пор, пока не будет "
        "реализована логика расчёта усушки в соответствии с пользовательской "
        "историей 2 - Расчёт усушки по упрощённой логике."
    )


def test_shrinkage_calculation_with_multiple_products():
    """
    Интеграционный тест: проверяет расчёт усушки для нескольких номенклатур
    с использованием разных стратегий расчёта.
    """
    # Подготовка данных для нескольких номенклатур
    test_products = [
        {
            "nomenclature": "Пиво светлое",
            "initial_balance": 1000.0,
            "final_balance": 995.0,
            "days_stored": 30,
            "coeffs": {"a": 0.001, "b": 0.05, "c": 0.0001},
        },
        {
            "nomenclature": "Пиво тёмное",
            "initial_balance": 800.0,
            "final_balance": 790.0,
            "days_stored": 45,
            "coeffs": {"a": 0.0015, "b": 0.04, "c": 0.002},
        },
    ]

    strategy = CompatibilityStrategy()
    results = []

    for product_data in test_products:
        # Подготовка данных для стратегии
        batch_data = {
            "initial_mass": product_data["initial_balance"],
            "days_stored": product_data["days_stored"],
        }

        # Выполняем расчёт усушки
        calculated_shrinkage = strategy.calculate(batch_data, product_data["coeffs"])

        # Рассчитываем отклонение
        expected_final_balance = product_data["initial_balance"] - calculated_shrinkage
        deviation = product_data["final_balance"] - expected_final_balance

        # Создаём результат
        result = ShrinkageCalculation(
            nomenclature=product_data["nomenclature"],
            calculated_shrinkage=calculated_shrinkage,
            actual_balance=product_data["final_balance"],
            deviation=deviation,
        )

        results.append(result)

    # Проверки
    assert len(results) == len(test_products)

    for i, result in enumerate(results):
        assert isinstance(result, ShrinkageCalculation)
        assert result.nomenclature == test_products[i]["nomenclature"]
        assert isinstance(result.calculated_shrinkage, (int, float))
        assert result.actual_balance == test_products[i]["final_balance"]
        assert isinstance(result.deviation, (int, float))
