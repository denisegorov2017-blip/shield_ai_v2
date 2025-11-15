"""
Доменные сущности: Движение и остаток по партии
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    date,
)


@dataclass
class BatchMovement:
    """Движение товара по партии"""

    nomenclature: str  # Номенклатура
    date: date  # Дата
    movement_type: str  # Тип движения
    quantity: float  # Количество
    warehouse: str  # Склад


@dataclass
class BatchBalance:
    """Остаток товара по партии"""

    nomenclature: str  # Номенклатура
    date: date  # Дата
    balance: float  # Остаток
    warehouse: str  # Склад
    batch: str  # Партия
