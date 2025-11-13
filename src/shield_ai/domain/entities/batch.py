"""
Доменная сущность: Партия товара
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Batch:
    """Партия товара с FIFO логикой"""

    id: Optional[int]
    product_id: int
    arrival_date: str  # DD.MM.YYYY
    arrival_datetime: datetime
    initial_qty: float
    remaining_qty: float

    def __post_init__(self) -> None:
        """Валидация"""
        if self.initial_qty < 0:
            raise ValueError("Начальное количество не может быть отрицательным")

        if self.remaining_qty < 0:
            raise ValueError("Остаток не может быть отрицательным")

        if self.remaining_qty > self.initial_qty:
            raise ValueError("Остаток не может превышать начальное количество")

    @property
    def sold_qty(self) -> float:
        """Проданное количество"""
        return self.initial_qty - self.remaining_qty

    @property
    def days_stored(self) -> int:
        """Дней с момента прихода"""
        return (datetime.now() - self.arrival_datetime).days

    def is_empty(self) -> bool:
        """Партия пустая?"""
        return self.remaining_qty <= 0.001
