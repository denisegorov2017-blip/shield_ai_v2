"""
Use Case: Расчет усушки по упрощенной логике

Этот модуль реализует use case для расчета усушки по упрощенной логике,
используя SimpleShrinkageStrategy. В соответствии с пользовательской историей 2
из спецификации, реализует расчет усушки без сложных FIFO-расчетов.
"""

from typing import (
    List,
    Optional,
)

from src.shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)
from src.shield_ai.domain.shrinkage.strategies import (
    ShrinkageCalculationStrategy,
    SimpleShrinkageStrategy,
)
from src.shield_ai.infrastructure.logging_config import (
    get_logger,
)


class CalibrateCoefficientsUseCase:
    """
    Use Case: Расчет усушки по упрощенной логике

    Класс, реализующий бизнес-логику расчета усушки по упрощенной логике
    на основе данных о движениях и остатках товара. Использует
    SimpleShrinkageStrategy для выполнения расчетов.

    Attributes:
        strategy: Стратегия расчета усушки
        logger: Логгер для отслеживания выполнения операций
    """

    def __init__(
        self,
        product_repository=None,
        calibration_data_repository=None,
        coefficient_repository=None,
        strategy: Optional[ShrinkageCalculationStrategy] = None
    ):
        """
        Инициализирует use case с репозиториями и стратегией расчета усушки.

        Args:
            product_repository: Репозиторий для работы с продуктами
            calibration_data_repository: Репозиторий для работы с данными калибровки
            coefficient_repository: Репозиторий для работы с коэффициентами
            strategy: Стратегия расчета усушки. Если не указана, используется SimpleShrinkageStrategy.
        """
        self.product_repository = product_repository
        self.calibration_data_repository = calibration_data_repository
        self.coefficient_repository = coefficient_repository
        self.strategy = strategy if strategy is not None else SimpleShrinkageStrategy()
        self.logger = get_logger(__name__)

    def execute(
        self, movements: List[BatchMovement], balances: List[BatchBalance]
    ) -> List[ShrinkageCalculation]:
        """
        Выполняет расчет усушки по упрощенной логике.

        Args:
            movements: Список движений товара
            balances: Список остатков товара

        Returns:
            Список результатов расчета усушки
        """
        self.logger.info(
            "Starting shrinkage calculation",
            movements_count=len(movements),
            balances_count=len(balances),
        )

        # Выполняем расчет усушки с помощью стратегии
        results = self.strategy.calculate_shrinkage(movements, balances)

        self.logger.info(
            "Shrinkage calculation completed successfully", results_count=len(results)
        )

        return results

    def execute_all(self) -> dict:
        """
        Выполняет калибровку коэффициентов для всех продуктов
        """
        if self.product_repository is None or self.calibration_data_repository is None or self.coefficient_repository is None:
            raise ValueError("Для выполнения калибровки необходимо инициализировать все репозитории")

        products = self.product_repository.get_all()
        results = {}

        for product in products:
            try:
                # Получаем данные для калибровки
                calibration_data = self.calibration_data_repository.get_for_product(product.id)
                
                # Выполняем калибровку (в реальной реализации здесь будет логика калибровки)
                # Пока возвращаем заглушку с коэффициентами
                coefficients = {
                    'a': 0.01,  # Пример коэффициента
                    'b': 0.05,  # Пример коэффициента
                    'c': 0.001, # Пример коэффициента
                    'status': 'success'
                }
                
                # Сохраняем коэффициенты
                from src.shield_ai.domain.entities.shrinkage_profile import ShrinkageCoefficient
                coefficient = ShrinkageCoefficient(
                    product_id=product.id,
                    a=coefficients['a'],
                    b=coefficients['b'],
                    c=coefficients['c']
                )
                self.coefficient_repository.save(coefficient)
                
                results[product.name] = coefficients
            except Exception as e:
                results[product.name] = {
                    'a': 0,
                    'b': 0,
                    'c': 0,
                    'status': f'error: {str(e)}'
                }

        return results
