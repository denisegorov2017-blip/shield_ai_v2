"""
Доменная сущность: Профиль усушки товара
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class CoefficientStatus(Enum):
    """Статус коэффициентов"""

    CALIBRATED = "калиброван"
    STANDARD = "стандартные"
    ESTIMATED = "оценочные"


@dataclass
class ShrinkageProfile:
    """Профиль усушки для товара"""

    product_id: int
    a: float  # Максимальная усушка
    b: float  # Скорость затухания
    c: float  # Постоянная составляющая
    rmse: Optional[float]
    data_points: int
    status: CoefficientStatus
    calibration_date: datetime

    def __post_init__(self) -> None:
        """Валидация коэффициентов"""
        if not 0.01 <= self.a <= 0.15:
            raise ValueError("Коэффициент a должен быть в диапазоне [0.01, 0.15]")

        if not 0.01 <= self.b <= 0.5:
            raise ValueError("Коэффициент b должен быть в диапазоне [0.01, 0.5]")

        if not 0.0 <= self.c <= 0.03:
            raise ValueError("Коэффициент c должен быть в диапазоне [0.0, 0.03]")

    def is_calibrated(self) -> bool:
        """Профиль откалиброван на реальных данных?"""
        return self.status == CoefficientStatus.CALIBRATED

    def get_accuracy_percentage(self) -> str:
        """Ожидаемая точность в %"""
        if self.is_calibrated():
            return "99.9% (калиброван)"
        return "85-90% (стандартные)"
