"""
Use Case: Аудит остатков

Данный модуль содержит реализацию use case для аудита остатков,
включая проверку на отрицательные значения и валидацию входных данных.
"""

from typing import (
    List,
)

from src.shield_ai.infrastructure.logging_config import (
    get_logger,
)

from src.shield_ai.domain.entities.batch import (
    BatchBalance,
)
from src.shield_ai.domain.exceptions import (
    ValidationException,
)

import logging


class AuditInventoryUseCase:
    """
    Use Case для аудита остатков.

    Выполняет проверку остатков на наличие отрицательных значений
    и валидацию входных данных.
    """

    def __init__(self):
        """
        Инициализирует use case аудита остатков.
        """
        self.logger = get_logger(self.__class__.__name__)

    def find_negative_balances(self, batches: List[BatchBalance]) -> List[BatchBalance]:
        """
        Находит отрицательные остатки в списке BatchBalance.

        Args:
            batches: Список объектов BatchBalance для проверки

        Returns:
            List[BatchBalance]: Список BatchBalance с отрицательными остатками

        Raises:
            ValidationException: При некорректных входных данных
        """
        self.logger.info("Starting to find negative balances", extra={"batch_count": len(batches)})
        self._validate_batches(batches)

        # Проверяем остатки на отрицательные значения
        negative_balances = []
        for batch in batches:
            if batch.balance < 0:
                self.logger.info(
                    "Negative balance detected",
                    extra={
                        "nomenclature": batch.nomenclature,
                        "batch": batch.batch,
                        "balance": batch.balance,
                        "warehouse": batch.warehouse,
                    }
                )
                negative_balances.append(batch)

        self.logger.info(
            "Negative balances search completed",
            extra={
                "negative_count": len(negative_balances),
                "total_count": len(batches),
            }
        )

        return negative_balances

    def execute(self, batch_balances: List[BatchBalance]) -> List[BatchBalance]:
        """
        Выполняет аудит остатков по партиям.

        Args:
            batch_balances: Список объектов BatchBalance для проверки

        Returns:
            List[BatchBalance]: Список BatchBalance с отрицательными остатками
            или пустой список, если таковых нет

        Raises:
            ValidationException: При некорректных входных данных
        """
        self.logger.info("Starting inventory audit", extra={"batch_count": len(batch_balances)})
        self._validate_batches(batch_balances)

        # Проверяем остатки на отрицательные значения
        negative_balances = []
        for batch_balance in batch_balances:
            if batch_balance.balance < 0:
                self.logger.info(
                    "Negative balance detected",
                    extra={
                        "nomenclature": batch_balance.nomenclature,
                        "batch": batch_balance.batch,
                        "balance": batch_balance.balance,
                        "warehouse": batch_balance.warehouse,
                    }
                )
                negative_balances.append(batch_balance)

        self.logger.info(
            "Inventory audit completed",
            extra={
                "negative_count": len(negative_balances),
                "total_count": len(batch_balances),
            }
        )

        return negative_balances

    def find_excess_balances(self, batches: List[BatchBalance]) -> List[BatchBalance]:
        """
        Находит излишки остатков в списке BatchBalance.

        Args:
            batches: Список объектов BatchBalance для проверки

        Returns:
            List[BatchBalance]: Список BatchBalance с излишками (остатки больше максимального порога)

        Raises:
            ValidationException: При некорректных входных данных
        """
        self.logger.info("Starting to find excess balances", extra={"batch_count": len(batches)})
        self._validate_batches(batches)

        # Проверяем остатки на превышение максимального порога (например, 9999)
        max_threshold = 9999  # порог для определения излишков
        excess_balances = []
        for batch in batches:
            if batch.balance > max_threshold:
                self.logger.info(
                    "Excess balance detected",
                    extra={
                        "nomenclature": batch.nomenclature,
                        "batch": batch.batch,
                        "balance": batch.balance,
                        "warehouse": batch.warehouse,
                    }
                )
                excess_balances.append(batch)

        self.logger.info(
            "Excess balances search completed",
            extra={
                "excess_count": len(excess_balances),
                "total_count": len(batches),
            }
        )

        return excess_balances

    def _validate_batches(self, batches: List[BatchBalance]) -> None:
        """
        Валидирует список BatchBalance.

        Args:
            batches: Список объектов BatchBalance для валидации

        Raises:
            ValidationException: При некорректных входных данных
        """
        # Проверяем, что список не пустой
        if not batches:
            self.logger.warning("Empty batches list provided")
            raise ValidationException(
                "Список остатков по партиям не может быть пустым",
                error_code="EMPTY_BATCHES",
            )

        # Проверяем, что все элементы являются объектами BatchBalance
        for i, batch in enumerate(batches):
            if not isinstance(batch, BatchBalance):
                self.logger.error(
                    "Invalid batch balance type",
                    extra={
                        "index": i,
                        "actual_type": type(batch).__name__,
                    }
                )
                raise ValidationException(
                    f"Элемент с индексом {i} не является объектом BatchBalance",
                    error_code="INVALID_BATCH_BALANCE_TYPE",
                )

            # Проверяем, что nomenclature не пустая
            if not batch.nomenclature or batch.nomenclature.strip() == "":
                self.logger.error(
                    "Empty nomenclature detected", extra={"index": i, "batch": batch.batch}
                )
                raise ValidationException(
                    f"Номенклатура не может быть пустой в элементе с индексом {i}",
                    error_code="EMPTY_NOMENCLATURE",
                )
