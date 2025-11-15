"""
Модуль реализации экспорта в формат JSON.

Содержит реализацию экспортера, который преобразует список объектов
ShrinkageCalculation в JSON-формат и записывает в файл.
"""

import json
from datetime import (
    date,
)
from typing import (
    Any,
    Dict,
    List,
)

from ...domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)
from ..export_interfaces import (
    Exporter,
)
from ..logging_config import (
    get_logger,
)


class JsonEncoder(json.JSONEncoder):
    """
    Кастомный JSON-энкодер для сериализации специфических типов данных.
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)


def _convert_to_dict(item: ShrinkageCalculation) -> dict:
    """
    Преобразует объект ShrinkageCalculation в словарь.

    Args:
        item: Объект ShrinkageCalculation

    Returns:
        Словарь с данными из объекта
    """
    return {
        "nomenclature": item.nomenclature,
        "calculated_shrinkage": item.calculated_shrinkage,
        "actual_balance": item.actual_balance,
        "deviation": item.deviation,
    }


class JsonExporter(Exporter):
    """
    Реализация экспорта данных ShrinkageCalculation в формат JSON.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def export(self, data: List[ShrinkageCalculation], output_path: str) -> None:
        """
        Экспортирует список объектов ShrinkageCalculation в JSON-файл.

        Args:
            data: Список объектов ShrinkageCalculation для экспорта
            output_path: Путь к файлу, в который нужно экспортировать данные
        """
        self.logger.info(
            "Начало экспорта в JSON", output_path=output_path, count=len(data)
        )

        try:
            # Преобразуем объекты ShrinkageCalculation в словари
            json_data = [_convert_to_dict(item) for item in data]

            # Записываем JSON в файл
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(
                    json_data, file, ensure_ascii=False, indent=2, cls=JsonEncoder
                )

            self.logger.info("Экспорт в JSON завершен успешно", output_path=output_path)

        except Exception as e:
            self.logger.error("Ошибка при экспорте в JSON", error=str(e))
            raise
