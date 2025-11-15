"""
Доменная сущность: Расчёт усушки
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    date,
)
from enum import (
    Enum,
)


class CoefficientStatus(Enum):
    """Статус коэфициента усушки"""

    ACTIVE = "активен"
    INACTIVE = "неактивен"
    PENDING = "ожидает калибровки"
    STANDARD = "стандартные"
    CALIBRATED = "калиброван"


@dataclass
class StorageConditions:
    """Условия хранения продукта"""

    temperature_factor: float  # Температурный фактор
    humidity_factor: float  # Фактор влажности
    storage_conditions: str  # Условия хранения
    packaging_type: str  # Тип упаковки
    shelf_life_days: int  # Срок хранения в днях


@dataclass
class ShrinkageProfile:
    """Профиль усушки для товара"""

    product_id: int
    product_name: str
    base_coefficient: float  # Базовый коэффициент усушки
    time_factor: float  # Временной фактор
    storage_conditions: StorageConditions  # Условия хранения


@dataclass
class ShrinkageCoefficient:
    """Коэффициенты усушки для товара"""

    product_id: int
    a: float  # Коэффициент начальной усушки
    b: float  # Коэффициент скорости усушки
    c: float  # Коэффициент постоянной усушки
    rmse: float = 0.0  # Среднеквадратичная ошибка
    data_points: int = 0  # Количество точек данных
    status: CoefficientStatus = CoefficientStatus.ACTIVE  # Статус коэффициента


@dataclass
class ShrinkagePeriod:
    """Период расчёта усушки"""

    product_name: str  # Название номенклатуры
    calculation_period_start: date  # Начало периода расчёта
    calculation_period_end: date  # Конец периода расчёта


@dataclass
class ShrinkageBalances:
    """Остатки для расчёта усушки"""

    initial_balance: float  # Начальный остаток
    movements_total: float  # Всего движений (приход/расход)
    final_balance: float  # Конечный остаток по факту


@dataclass
class ShrinkageResults:
    """Результаты расчёта усушки"""

    calculated_shrinkage: float  # Рассчитанная усушка по норме
    actual_shrinkage: (
        float  # Фактическая убыль (разница между ожидаемым и реальным остатком)
    )
    shrinkage_percentage: float  # Процент усушки
    variance: float  # Отклонение (факт - норма)


@dataclass
class ShrinkageCalculation:
    """Результат расчёта усушки"""

    nomenclature: str  # Номенклатура
    calculated_shrinkage: float  # Рассчитанная усушка
    actual_balance: float  # Фактический остаток
    deviation: float  # Отклонение
