"""
Три стратегии расчёта усушки согласно документации
ЧИСТАЯ бизнес-логика без зависимостей

Этот модуль реализует три различные стратегии расчета усушки:
1. Порционная модель (99.9% точность) - используется для калибровки
2. Взвешенная интегральная модель (99.5% точность) - используется для прогнозов
3. Модель совместимости (85-90% точность) - для быстрых оценок и legacy систем

Каждая стратегия реализует абстрактный класс ShrinkageStrategy и предоставляет
различные подходы к вычислению усушки в зависимости от требуемой точности и
доступных данных.
"""

import math
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, List, Type


class ShrinkageStrategy(ABC):
    """
    Базовая стратегия расчёта усушки

    Абстрактный класс, определяющий интерфейс для всех стратегий расчета усушки.
    Все реализации должны предоставить методы для вычисления усушки, получения
    названия стратегии и ожидаемой точности. Это позволяет использовать разные
    подходы к расчету усушки в зависимости от требований к точности и доступным
    данным.
    """

    @abstractmethod
    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        """
        Рассчитывает усушку для партии

        Args:
            batch_data: Данные партии, содержащие информацию о начальной массе,
                       датах прибытия/продаж и других параметрах, необходимых
                       для расчета усушки по конкретной стратегии
            coeffs: Коэффициенты (a, b, c), используемые в формулах расчета усушки

        Returns:
            Усушка в кг
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Возвращает название стратегии

        Returns:
            Название стратегии в виде строки
        """

    @abstractmethod
    def get_accuracy(self) -> str:
        """
        Возвращает ожидаемую точность стратегии

        Returns:
            Ожидаемая точность в виде строки (например, "99.9%")
        """


class PortionStrategy(ShrinkageStrategy):
    """
    ПОРЦИОННАЯ МОДЕЛЬ (99.9% точность)

    Используется для калибровки коэффициентов.
    Каждая продажа - отдельная порция со своим временем хранения.

    Формула: Усушка_порции = m * [a * (1 - e^(-b*t)) + c]

    Математическое объяснение:
    - a: начальная скорость усушки (коэффициент при экспоненте)
    - b: скорость затухания усушки (коэффициент в экспоненте)
    - c: базовый уровень усушки (минимальная усушка независимо от времени)
    - t: время хранения в днях
    - m: масса проданного товара

    Формула (1 - e^(-b*t)) моделирует накопленную усушку за время хранения,
    начиная с нуля и асимптотически приближаясь к 1. Умножение на a дает
    масштаб усушки, а добавление c обеспечивает минимальный уровень усушки.
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        """
        Рассчитывает усушку по порционной модели

        Для каждой продажи в данных партии вычисляет усушку по формуле:
        усушка_порции = количество_проданного * [a * (1 - e^(-b * дни_хранения)) + c]

        Args:
            batch_data: Данные партии, содержащие:
                       - arrival_date: дата прибытия партии
                       - sales: список продаж с датами и количествами
            coeffs: Коэффициенты a, b, c для расчета усушки

        Returns:
            Общая усушка для всех продаж в партии
        """
        a, b, c = coeffs["a"], coeffs["b"], coeffs["c"]
        arrival_date = batch_data["arrival_date"]
        sales = batch_data.get("sales", [])

        total_shrinkage = 0.0

        for sale in sales:
            # Вычисление количества дней между датой продажи и датой прибытия партии
            days = (sale["date"] - arrival_date).days
            if days < 0:
                # Пропускаем продажи, которые произошли до прибытия партии
                continue

            # Расчет усушки для одной порции по формуле: m * [a * (1 - e^(-b*t)) + c]
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

    Математическое объяснение:
    - a, b: коэффициенты из модели усушки
    - M0: начальная масса партии
    - shrinkage_rate = M0 * a * b * e^(-b * day_counter) - скорость усушки
    - mass_ratio = current_mass / M0 - коэффициент, учитывающий уменьшающуюся массу
    - daily_shrinkage = shrinkage_rate * mass_ratio - суточная усушка с учетом текущей массы

    Модель учитывает, что усушка зависит от текущей массы товара, что делает
    расчет более точным по сравнению с простыми моделями, где усушка
    рассчитывается от начальной массы на протяжении всего периода.
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        """
        Рассчитывает усушку по взвешенной интегральной модели

        Алгоритм:
        1. Инициализирует начальные параметры (масса, даты, счетчики)
        2. Для каждого дня в периоде:
           - Вычисляет скорость усушки на основе начальной массы и экспоненты
           - Применяет коэффициент массы для учета текущего остатка
           - Обновляет общую усушку и текущую массу
           - Учитывает продажи в этот день
        3. Возвращает общую усушку за период

        Args:
            batch_data: Данные партии, содержащие:
                       - initial_mass: начальная масса партии
                       - arrival_date: дата прибытия партии
                       - end_date: конечная дата расчета
                       - daily_sales: словарь продаж по дням (опционально)
            coeffs: Коэффициенты a, b для расчета усушки

        Returns:
            Общая усушка за период
        """
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
            # Вычисление скорости усушки: M0 * a * b * e^(-b * day_counter)
            # Это производная от функции усушки по времени
            shrinkage_rate = M0 * a * b * math.exp(-b * day_counter)
            # Учет текущей массы: усушка пропорциональна текущему остатку
            mass_ratio = current_mass / M0 if M0 > 0 else 0
            # Суточная усушка с учетом текущей массы
            daily_shrinkage = shrinkage_rate * mass_ratio

            total_shrinkage += daily_shrinkage
            current_mass -= daily_shrinkage

            # Учет продаж в текущий день
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

    Математическое объяснение:
    - a: начальная скорость усушки
    - b: скорость затухания усушки
    - c: базовый уровень усушки
    - M0: начальная масса партии
    - T: общее время хранения в днях
    - Формула: M0 * [a * (1 - e^(-b*T)) + c]

    Эта модель дает приближенную оценку усушки для всей партии за весь
    период хранения без учета временных аспектов продаж. Подходит для
    быстрых расчетов, когда точное время продаж неизвестно или несущественно.
    """

    def calculate(self, batch_data: Dict[str, Any], coeffs: Dict[str, float]) -> float:
        """
        Рассчитывает усушку по модели совместимости

        Простая модель, вычисляющая усушку для всей партии за весь период
        хранения без учета временных аспектов продаж. Формула применяется
        к начальной массе с учетом общего времени хранения.

        Args:
            batch_data: Данные партии, содержащие:
                       - initial_mass: начальная масса партии
                       - days_stored: общее время хранения в днях
            coeffs: Коэффициенты a, b, c для расчета усушки

        Returns:
            Усушка для всей партии за весь период хранения
        """
        a, b, c = coeffs["a"], coeffs["b"], coeffs["c"]
        M0 = batch_data["initial_mass"]
        T = batch_data["days_stored"]

        # Формула: M0 * [a * (1 - e^(-b*T)) + c]
        # где M0 - начальная масса, T - общее время хранения
        shrinkage: float = M0 * (a * (1 - math.exp(-b * T)) + c)
        return shrinkage

    def get_name(self) -> str:
        return "Совместимости"

    def get_accuracy(self) -> str:
        return "85-90%"


class StrategyFactory:
    """
    Фабрика стратегий

    Класс, отвечающий за создание экземпляров различных стратегий расчета усушки.
    Реализует паттерн "Фабрика" для централизованного создания стратегий по
    их именам. Позволяет легко добавлять новые стратегии и управлять их
    созданием в различных частях приложения.
    """

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
            strategy_name: Имя стратегии ('portion', 'weighted', или 'final')

        Returns:
            Экземпляр соответствующей стратегии

        Raises:
            ValueError: Если указана неизвестная стратегия
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
        """
        Возвращает список всех доступных стратегий

        Returns:
            Список имен всех зарегистрированных стратегий
        """
        return list(cls._strategies.keys())
