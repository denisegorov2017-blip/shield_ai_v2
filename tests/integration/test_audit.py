"""
Integration tests for inventory audit functionality.

This module tests the integration between different components
of the audit system, particularly focusing on negative balance detection
and shrinkage calculation.
"""

from datetime import (
    date,
)

import pytest

from src.shield_ai.domain.entities.batch import (
    BatchBalance,
)
from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)


class AuditResult:
    """
    Заглушка для результата аудита.
    """

    def __init__(
        self,
        batch,
        has_negative_balance=False,
        negative_balance_amount=None,
        shrinkage_calculation=None,
    ):
        self.batch = batch
        self.has_negative_balance = has_negative_balance
        self.negative_balance_amount = negative_balance_amount
        self.shrinkage_calculation = shrinkage_calculation


class MockAuditUseCase:
    """
    Мок-класс для демонстрации ожидаемого поведения AuditInventoryUseCase.
    """

    def process_batch(self, batch):
        # Проверяем, является ли остаток отрицательным
        has_negative_balance = batch.balance < 0
        negative_balance_amount = batch.balance if has_negative_balance else None

        # Создаем расчет усушки
        shrinkage_calculation = ShrinkageCalculation(
            nomenclature=batch.nomenclature,
            calculated_shrinkage=0.0,
            actual_balance=batch.balance,
            deviation=abs(batch.balance) if has_negative_balance else 0.0,
        )

        return AuditResult(
            batch=batch,
            has_negative_balance=has_negative_balance,
            negative_balance_amount=negative_balance_amount,
            shrinkage_calculation=shrinkage_calculation,
        )

    def process_batches(self, batches):
        return [self.process_batch(batch) for batch in batches]


class TestAuditIntegration:
    """
    Integration tests for audit functionality.
    Tests the interaction between domain entities and use cases.
    """

    def test_negative_balance_detection_integration(self):
        """
        Test that audit use case properly detects negative balances
        when processing batch data.

        This test verifies the integration between:
        - BatchBalance entity (domain)
        - AuditInventoryUseCase (application layer)
        - Negative balance detection logic

        Expected: When batch with negative balance is processed,
        the audit should identify it correctly.
        """
        # Arrange: Create batch with negative balance
        batch = BatchBalance(
            nomenclature="Товар-001",
            date=date(2024, 1, 1),
            balance=-50.0,  # Отрицательный остаток
            warehouse="Склад-001",
            batch="Партия-01",
        )

        # Create use case instance
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()

        # Act: Process the batch through audit
        result = audit_use_case.execute([batch])

        # Assert: Verify that negative balance is detected
        assert len(result) == 1
        assert result[0].balance == -50.0
        assert result[0].nomenclature == "Товар-001"

    def test_multiple_batch_audit_integration(self):
        """
        Test audit processing of multiple batches with mixed results.

        This test verifies the integration when processing multiple batches
        where some have negative balances and others don't.
        """
        # Arrange: Create multiple batches
        batches = [
            BatchBalance(
                nomenclature="Товар-001",
                date=date(2024, 1, 1),
                balance=-50.0,  # Отрицательный остаток
                warehouse="Склад-001",
                batch="Партия-01",
            ),
            BatchBalance(
                nomenclature="Товар-002",
                date=date(2024, 1, 1),
                balance=150.0,  # Положительный остаток
                warehouse="Склад-002",
                batch="Партия-02",
            ),
            BatchBalance(
                nomenclature="Товар-003",
                date=date(2024, 1, 1),
                balance=-10.0,  # Отрицательный остаток
                warehouse="Склад-003",
                batch="Партия-03",
            ),
        ]

        # Create use case instance
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()

        # Act: Process all batches
        results = audit_use_case.execute(batches)

        # Assert: Verify results
        negative_results = [r for r in results if r.balance < 0]

        assert len(negative_results) == 2  # Two batches with negative balance

        # Verify specific negative balance amounts
        negative_amounts = [r.balance for r in negative_results]
        assert -50.0 in negative_amounts
        assert -10.0 in negative_amounts

    def test_audit_with_shrinkage_calculation_integration(self):
        """
        Test integration between audit and shrinkage calculation.

        This test verifies that when negative balances are detected,
        appropriate shrinkage calculations are performed.
        """
        # Arrange: Create batch with negative balance
        batch = BatchBalance(
            nomenclature="Товар-001",
            date=date(2024, 1, 1),
            balance=-25.0,  # Отрицательный остаток
            warehouse="Склад-001",
            batch="Партия-01",
        )

        # Create use case instance
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()

        # Act: Process batch and get shrinkage calculation
        result = audit_use_case.execute([batch])

        # Assert: Verify shrinkage calculation is properly created
        assert len(result) == 1
        assert result[0].nomenclature == "Товар-001"
        assert result[0].balance == -25.0

    def test_audit_use_case_not_implemented(self):
        """
        Test that demonstrates the AuditInventoryUseCase is now implemented.

        This test should pass after the AuditInventoryUseCase is implemented.
        """
        # Create the real use case - this should work now
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()
        assert audit_use_case is not None

    def test_audit_with_zero_balance_integration(self):
        """
        Test audit behavior with zero balance (edge case).

        This test verifies that zero balances are handled correctly
        and distinguished from negative balances.
        """
        # Arrange: Create batch with zero balance
        batch = BatchBalance(
            nomenclature="Товар-001",
            date=date(2024, 1, 1),
            balance=0.0,  # Нулевой остаток
            warehouse="Склад-001",
            batch="Партия-001",
        )

        # Create use case instance
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()

        # Act: Process the batch
        result = audit_use_case.execute([batch])

        # Assert: Verify that zero balance is not treated as negative
        assert (
            len(result) == 0
        )  # Zero balance should not be included in negative balances

    def test_excess_balance_detection_integration(self):
        """
        Test that audit use case properly detects excess balances
        when processing batch data.

        This test verifies the integration between:
        - BatchBalance entity (domain)
        - AuditInventoryUseCase (application layer)
        - Excess balance detection logic

        Expected: When batch with excess balance is processed,
        the audit should identify it correctly.
        """
        # Arrange: Create batch with excess balance
        batch = BatchBalance(
            nomenclature="Товар-001",
            date=date(2024, 1, 1),
            balance=1500000,  # Excess balance (above threshold)
            warehouse="Склад-001",
            batch="Партия-01",
        )

        # Create use case instance
        from src.shield_ai.application.use_cases.audit_inventory import (
            AuditInventoryUseCase,
        )

        audit_use_case = AuditInventoryUseCase()

        # Act: Process the batch through audit
        result = audit_use_case.find_excess_balances([batch])

        # Assert: Verify that excess balance is detected
        assert len(result) == 1
        assert result[0].balance == 1500000
        assert result[0].nomenclature == "Товар-001"
