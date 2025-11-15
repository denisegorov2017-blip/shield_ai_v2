"""
Модуль реализации экспорта в формат Markdown.

Содержит реализацию экспортера, который преобразует список объектов
ShrinkageCalculation в Markdown-формат и записывает в файл.
"""

from typing import (
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


def _format_markdown_row(item: ShrinkageCalculation) -> str:
    """
    Форматирует строку данных для Markdown-таблицы.

    Args:
        item: Объект ShrinkageCalculation

    Returns:
        Форматированная строка для таблицы
    """
    return f"| {item.nomenclature} | {item.calculated_shrinkage} | {item.actual_balance} | {item.deviation} |"


def _create_markdown_content(data: List[ShrinkageCalculation]) -> str:
    """
    Создает Markdown-контент из списка данных.

    Args:
        data: Список объектов ShrinkageCalculation

    Returns:
        Сформированный Markdown-контент
    """
    content = "# Отчет по усушке\n\n"
    content += "## Результаты расчета усушки\n\n"

    # Создаем заголовок таблицы
    content += (
        "| Номенклатура | Рассчитанная усушка | Фактический остаток | Отклонение |\n"
    )
    content += "|-------------|------------------|------------------|----------|\n"

    # Добавляем строки с данными
    for item in data:
        content += _format_markdown_row(item) + "\n"

    # Добавляем дополнительную информацию
    content += f"\n*Всего записей: {len(data)}*\n"

    return content


class MarkdownExporter(Exporter):
    """
    Реализация экспорта данных ShrinkageCalculation в формат Markdown.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def export(self, data: List[ShrinkageCalculation], output_path: str) -> None:
        """
        Экспортирует список объектов ShrinkageCalculation в Markdown-файл.

        Args:
            data: Список объектов ShrinkageCalculation для экспорта
            output_path: Путь к файлу, в который нужно экспортировать данные
        """
        self.logger.info(
            "Начало экспорта в Markdown", output_path=output_path, count=len(data)
        )

        try:
            markdown_content = _create_markdown_content(data)

            # Записываем Markdown в файл
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(markdown_content)

            self.logger.info(
                "Экспорт в Markdown завершен успешно", output_path=output_path
            )

        except Exception as e:
            self.logger.error("Ошибка при экспорте в Markdown", error=str(e))
            raise
