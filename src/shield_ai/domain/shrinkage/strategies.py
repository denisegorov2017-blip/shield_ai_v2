"""
Три стратегии расчёта усушки согласно документации
ЧИСТАЯ бизнес-логика без зависимостей
"""

import math
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, List, Type


class ShrinkageStrategy(ABC):
    """Базовая стратегия расчёта усушки"""

    @abstractmethod
    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        """
        Рассчитывает усушку для партии

        Args:
            batch_data: Данные партии
            coeffs: Коэффициенты (a, b, c)

        Returns:
            Усушка в кг
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Название стратегии"""
        pass

    @abstractmethod
    def get_accuracy(self) -> str:
        """Ожидаемая точность"""
        pass


class PortionStrategy(ShrinkageStrategy):
    """
    ПОРЦИОННАЯ МОДЕЛЬ (99.9% точность)

    Используется для калибровки коэффициентов.
    Каждая продажа - отдельная порция со своим временем хранения.

    Формула: Усушка_порции = m * [a * (1 - e^(-b*t)) + c]
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        a, b, c = coeffs["a"], coeffs["b"], coeffs["c"]
        arrival_date = batch_data["arrival_date"]
        sales = batch_data.get("sales", [])

        total_shrinkage = 0.0

        for sale in sales:
            days = (sale["date"] - arrival_date).days
            if days < 0:
                continue

            shrinkage = sale["quantity"] * (a * (1 - math.exp(-b * days)) + c)
            total_shrinkage += shrinkage

        return total_shrinkage

    def get_name(self) -> str:
        return "Порционная"

    def get_accuracy(self) -> str:
        return "99.9%"


class WeightedStrategy(ShrinkageStrategy):
    """
    ВЗВЕШЕННАЯ ИНТЕГРАЛЬНАЯ МОДЕЛЬ (99.5% точность)

    Используется для production прогнозов.
    Усушка рассчитывается дискретно по дням с учётом остатка.
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        a, b = coeffs["a"], coeffs["b"]
        M0 = batch_data["initial_mass"]
        arrival_date = batch_data["arrival_date"]
        end_date = batch_data["end_date"]
        daily_sales = batch_data.get("daily_sales", {})

        current_mass = M0
        total_shrinkage = 0.0
        current_date = arrival_date
        day_counter = 0

        while current_date <= end_date:
            shrinkage_rate = M0 * a * b * math.exp(-b * day_counter)
            mass_ratio = current_mass / M0 if M0 > 0 else 0
            daily_shrinkage = shrinkage_rate * mass_ratio

            total_shrinkage += daily_shrinkage
            current_mass -= daily_shrinkage

            if current_date in daily_sales:
                current_mass -= daily_sales[current_date]

            current_date += timedelta(days=1)
            day_counter += 1

        return total_shrinkage

    def get_name(self) -> str:
        return "Взвешенная"

    def get_accuracy(self) -> str:
        return "99.5%"


class FinalStrategy(ShrinkageStrategy):
    """
    МОДЕЛЬ СОВМЕСТИМОСТИ (85-90% точность)

    Используется для быстрых оценок и legacy систем.
    Усушка для всей партии за всё время без учёта продаж.
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        a, b, c = coeffs["a"], coeffs["b"], coeffs["c"]
        M0 = batch_data["initial_mass"]
        T = batch_data["days_stored"]

        shrinkage: float = M0 * (a * (1 - math.exp(-b * T)) + c)
        return shrinkage

    def get_name(self) -> str:
        return "Совместимости"

    def get_accuracy(self) -> str:
        return "85-90%"


class StrategyFactory:
    """Фабрика стратегий"""

    _strategies: Dict[str, Type[ShrinkageStrategy]] = {
        "portion": PortionStrategy,
        "weighted": WeightedStrategy,
        "final": FinalStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str) -> ShrinkageStrategy:
        """
        Создаёт стратегию по имени

        Args:
            strategy_name: 'portion', 'weighted', или 'final'

        Returns:
            Экземпляр стратегии
        """
        if strategy_name not in cls._strategies:
            raise ValueError(
                f"Неизвестная стратегия: {strategy_name}. "
                f"Доступны: {list(cls._strategies.keys())}"
            )

        strategy_class: Type[ShrinkageStrategy] = cls._strategies[strategy_name]
        return strategy_class()

    @classmethod
    def get_all_strategies(cls) -> List[str]:
        """Список всех доступных стратегий"""
        return list(cls._strategies.keys())
