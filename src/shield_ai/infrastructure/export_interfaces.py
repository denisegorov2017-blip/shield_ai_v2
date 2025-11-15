from typing import (
    List,
    Protocol,
)

from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)


class Exporter(Protocol):
    """
    Протокол для экспорта данных ShrinkageCalculation в различные форматы.
    """

    def export(self, data: List[ShrinkageCalculation], output_path: str) -> None:
        """
        Экспортирует список объектов ShrinkageCalculation в файл по указанному пути.

        Args:
            data: Список объектов ShrinkageCalculation для экспорта
            output_path: Путь к файлу, в который нужно экспортировать данные
        """
        ...
