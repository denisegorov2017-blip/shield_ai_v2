"""
Три стратегии расчёта усушки согласно документации
ЧИСТАЯ бизнес-логика без зависимостей

Этот модуль реализует три различные стратегии расчета усушки:
1. Порционная модель (99.9% точность) - используется для калибровки
2. Взвешенная интегральная модель (99.5% точность) - используется для прогнозов
3. Модель совместимости (85-90% точность) - для быстрых оценок и legacy систем
4. Простая стратегия (упрощенный расчет усушки) - для упрощенного учета

Каждая стратегия реализует абстрактный класс ShrinkageStrategy и предоставляет
различные подходы к вычислению усушки в зависимости от требуемой точности и
доступных данных.
"""

import math
from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    timedelta,
)
from typing import (
    Any,
    Dict,
    List,
    Type,
)

from src.shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)


class ShrinkageStrategy(ABC):
    """
    Базовая стратегия расчёта усушки

    Абстрактный класс, определяющий интерфейс для всех стратегии расчета усушки.
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
    ПОРЦИОННАЯ МОДЕЛЬ (9.9% точность)

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
        coefficient_a = coeffs["a"]
        coefficient_b = coeffs["b"]
        coefficient_c = coeffs["c"]
        arrival_date = batch_data["arrival_date"]
        sales = batch_data.get("sales", [])

        total_shrinkage = 0.0

        for sale in sales:
            # Вычисление количества дней между датой продажи и датой прибытия партии
            storage_days = (sale["date"] - arrival_date).days
            if storage_days < 0:
                # Пропускаем продажи, которые произошли до прибытия партии
                continue

            # Расчет усушки для одной порции по формуле: m * [a * (1 - e^(-b*t)) + c]
            portion_shrinkage = sale["quantity"] * (
                coefficient_a * (1 - math.exp(-coefficient_b * storage_days))
                + coefficient_c
            )
            total_shrinkage += portion_shrinkage

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
        # Извлечение параметров из batch_data
        coefficient_a = coeffs["a"]
        coefficient_b = coeffs["b"]
        initial_mass = batch_data["initial_mass"]
        current_mass = initial_mass
        arrival_date = batch_data["arrival_date"]
        end_date = batch_data["end_date"]
        daily_sales = batch_data.get("daily_sales", {})

        # Инициализация переменных для цикла
        current_date = arrival_date
        day_counter = 0
        total_shrinkage = 0.0

        while current_date <= end_date:
            # Вычисление скорости усушки: initial_mass * a * b * e^(-b * day_counter)
            # Это производная от функции усушки по времени
            shrinkage_rate = (
                initial_mass
                * coefficient_a
                * coefficient_b
                * math.exp(-coefficient_b * day_counter)
            )
            # Учет текущей массы: усушка пропорциональна текущему остатку
            mass_ratio = current_mass / initial_mass if initial_mass > 0 else 0
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


class CompatibilityStrategy(ShrinkageStrategy):
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
        coefficient_a = coeffs["a"]
        coefficient_b = coeffs["b"]
        coefficient_c = coeffs["c"]
        initial_mass = batch_data["initial_mass"]
        storage_days = batch_data["days_stored"]

        # Формула: initial_mass * [a * (1 - e^(-b*T)) + c]
        # где initial_mass - начальная масса, storage_days - общее время хранения
        shrinkage: float = initial_mass * (
            coefficient_a * (1 - math.exp(-coefficient_b * storage_days))
            + coefficient_c
        )
        return shrinkage

    def get_name(self) -> str:
        return "Совместимости"

    def get_accuracy(self) -> str:
        return "85-90%"


class ShrinkageCalculationStrategy(ABC):
    """
    Протокол для стратегии расчета усушки на основе BatchMovement и BatchBalance

    Этот интерфейс определяет метод для упрощенного расчета усушки,
    который принимает списки движений и остатков, и возвращает результаты
    в виде списка ShrinkageCalculation.
    """

    @abstractmethod
    def calculate_shrinkage(
        self, movements: List[BatchMovement], balances: List[BatchBalance]
    ) -> List[ShrinkageCalculation]:
        """
        Рассчитывает усушку на основе данных о движениях и остатках

        Args:
            movements: Список движений товара
            balances: Список остатков товара

        Returns:
            Список результатов расчета усушки
        """

    @abstractmethod
    def get_coefficients(self) -> dict:
        """
        Возвращает коэффициенты усушки для данной стратегии

        Returns:
            dict: Словарь с коэффициентами усушки
        """
        """
        Рассчитывает усушку на основе данных о движениях и остатках

        Args:
            movements: Список движений товара
            balances: Список остатков товара

        Returns:
            Список результатов расчета усушки
        """


class SimpleShrinkageStrategy(ShrinkageCalculationStrategy):
    """
    Простая стратегия расчета усушки

    Упрощенная логика расчета усушки без сложной логики FIFO.
    Рассчитывает усушку как разницу между ожидаемым и фактическим остатками.
    """

    # Константы для типов движений
    IN_MOVEMENT_TYPES = {"приход", "in", "receipt", "поступление"}
    OUT_MOVEMENT_TYPES = {"расход", "out", "shipment", "продажа"}
    """
    Простая стратегия расчета усушки
    
    Упрощенная логика расчета усушки без сложной логики FIFO.
    Рассчитывает усушку как разницу между ожидаемым и фактическим остатками.
    """

    def get_coefficients(self) -> dict:
        """
        Возвращает коэффициенты усушки для простой стратегии.
        В простой стратегии коэфициенты не используются, возвращаем пустой словарь.
        
        Returns:
            dict: Пустой словарь коэффициентов
        """
        return {}

    def calculate_shrinkage(
        self, movements: List[BatchMovement], balances: List[BatchBalance]
    ) -> List[ShrinkageCalculation]:
        """
        Рассчитывает усушку по упрощенной логике

        Алгоритм:
        1. Для каждой номенклатуры суммируем все движения (приходы и расходы)
        2. Находим начальный и конечный остатки
        3. Рассчитываем ожидаемый остаток как начальный остаток + приход - расход
        4. Усушка = ожидаемый остаток - фактический остаток
        5. Отклонение = усушка / ожидаемый остаток (если ожидаемый остаток > 0)

        Args:
            movements: Список движений товара
            balances: Список остатков товара

        Returns:
            Список результатов расчета усушки
        """
        results = []

        # Группируем движения по номенклатуре
        movement_by_nomenclature = {}
        for movement in movements:
            if movement.nomenclature not in movement_by_nomenclature:
                movement_by_nomenclature[movement.nomenclature] = []
            movement_by_nomenclature[movement.nomenclature].append(movement)

        # Группируем остатки по номенклатуре
        balance_by_nomenclature = {}
        for balance in balances:
            if balance.nomenclature not in balance_by_nomenclature:
                balance_by_nomenclature[balance.nomenclature] = []
            balance_by_nomenclature[balance.nomenclature].append(balance)

        # Рассчитываем усушку для каждой номенклатуры
        for nomenclature in set(movement_by_nomenclature.keys()) | set(
            balance_by_nomenclature.keys()
        ):
            movements_for_nom = movement_by_nomenclature.get(nomenclature, [])
            balances_for_nom = balance_by_nomenclature.get(nomenclature, [])

            # Рассчитываем суммарные движения (приход и расход)
            total_in = sum(
                m.quantity
                for m in movements_for_nom
                if m.movement_type.lower() in self.IN_MOVEMENT_TYPES
            )
            total_out = sum(
                m.quantity
                for m in movements_for_nom
                if m.movement_type.lower() in self.OUT_MOVEMENT_TYPES
            )

            # Находим начальный и конечный остатки
            if balances_for_nom:
                # Сортируем остатки по дате, чтобы определить начальный и конечный
                sorted_balances = sorted(balances_for_nom, key=lambda x: x.date)
                initial_balance = sorted_balances[0].balance
                final_balance = sorted_balances[-1].balance
            else:
                initial_balance = 0
                final_balance = 0

            # Рассчитываем ожидаемый остаток
            expected_balance = initial_balance + total_in - total_out

            # Рассчитываем усушку как разницу между ожидаемым и фактическим остатками
            calculated_shrinkage = expected_balance - final_balance

            # Рассчитываем отклонение
            deviation = 0
            if expected_balance != 0:
                deviation = calculated_shrinkage / abs(expected_balance)

            # Создаем результат расчета
            result = ShrinkageCalculation(
                nomenclature=nomenclature,
                calculated_shrinkage=calculated_shrinkage,
                actual_balance=final_balance,
                deviation=deviation,
            )

            results.append(result)

        return results


class StrategyFactory:
    """
    Фабрика стратегий

    Класс, отвечающий за создание экземпляров различных стратегий расчета усушки.
    Реализует паттерн "Фабрика" для централизованного создания стратегий по
    их именам. Позволяет легко добавлять новые стратегии и управлять их
    созданием в различных частях приложения.
    """

    # Словарь доступных стратегий
    _strategies: Dict[str, Type[ShrinkageStrategy]] = {
        "portion": PortionStrategy,
        "weighted": WeightedStrategy,
        "compatibility": CompatibilityStrategy,
    }

    _strategies: Dict[str, Type[ShrinkageStrategy]] = {
        "portion": PortionStrategy,
        "weighted": WeightedStrategy,
        "compatibility": CompatibilityStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str) -> ShrinkageStrategy:
        """
        Создаёт стратегию по имени

        Args:
            strategy_name: Имя стратегии ('portion', 'weighted', или 'compatibility')

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
