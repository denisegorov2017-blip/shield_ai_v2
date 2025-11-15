"""
Модуль централизованной конфигурации логирования для проекта Shield AI.

Этот модуль настраивает logging для вывода логов в JSON-формате
в соответствии с требованиями конституции проекта.
"""

import json
import logging
from typing import (
    Any,
)


class JsonFormatter(logging.Formatter):
    """
    Кастомный форматтер для вывода логов в формате JSON.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Добавляем дополнительные атрибуты, если они есть
        if hasattr(record, "funcName"):
            log_entry["function"] = record.funcName
        if hasattr(record, "filename"):
            log_entry["file"] = record.filename
        if hasattr(record, "lineno"):
            log_entry["line"] = str(record.lineno)

        # Добавляем exception info, если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Добавляем stack info, если есть
        if record.stack_info:
            log_entry["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_entry, ensure_ascii=False)


def configure_logging() -> None:
    """
    Настраивает централизованное логирование для приложения.

    Конфигурация включает:
    - Вывод логов в JSON-формате
    - Использование стандартного модуля logging
    - Настройку уровней логирования
    """
    # Создаем форматтер для JSON логов
    json_formatter = JsonFormatter()

    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Удаляем все существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Создаем и настраиваем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)

    # Добавляем обработчик к корневому логгеру
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> Any:
    """
    Возвращает настроенный логгер с указанным именем.

    Args:
        name: Имя логгера (обычно __name__ модуля)

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    return logger


def set_log_level(level: int) -> None:
    """
    Устанавливает уровень логирования для корневого логгера.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(level)
