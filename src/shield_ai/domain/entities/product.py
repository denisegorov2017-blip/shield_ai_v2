"""
Доменная сущность: Товар
Чистая бизнес-логика без зависимостей от фреймворков
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)
from typing import (
    Optional,
)


@dataclass
class Product:
    """Товар в системе"""

    id: Optional[int]
    name: str
    group_name: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Валидация после инициализации"""
        if not self.name or not self.name.strip():
            raise ValueError("Название товара не может быть пустым")

        if len(self.name) > 500:
            raise ValueError("Название товара слишком длинное (макс 500 символов)")

    def __str__(self) -> str:
        return f"Product(id={self.id}, name='{self.name}')"
