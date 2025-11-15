"""
Скрипт для тестирования калибровки коэффициентов
"""

import os
import sys
from datetime import (
    datetime,
)
from typing import (
    Any,
    Dict,
    List,
)

# Добавляем директорию src в путь Python для корректных импортов
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

# Импорты после изменения sys.path
from shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from shield_ai.domain.entities.product import (
    Product,
)
from shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCoefficient,
)
from shield_ai.domain.repositories import (
    CalibrationDataRepository,
    CoefficientRepository,
    ProductRepository,
)

# Mock Repositories


class MockProductRepository(ProductRepository):
    def get_all(self) -> List[Product]:
        return [
            Product(
                id=1,
                name="Mock Product",
                group_name="Mock Group",
                created_at=datetime.now(),
            )
        ]


class MockCalibrationDataRepository(CalibrationDataRepository):
    def get_for_product(self, product_id: int) -> List[Dict[str, Any]]:
        return []


class MockCoefficientRepository(CoefficientRepository):
    def save(self, coeffs: ShrinkageCoefficient) -> None:
        pass


def test_calibration():
    product_repo = MockProductRepository()
    calibration_repo = MockCalibrationDataRepository()
    coefficient_repo = MockCoefficientRepository()
    use_case = CalibrateCoefficientsUseCase(
        product_repository=product_repo,
        calibration_data_repository=calibration_repo,
        coefficient_repository=coefficient_repo,
    )
    results = use_case.execute_all()
    print("Калибровка завершена:", len(results), "товаров")
    for product_name, coeffs in results.items():
        print(
            f"  {product_name}: a={coeffs['a']:.4f}, b={coeffs['b']:.4f}, c={coeffs['c']:.4f}, статус={coeffs['status']}"
        )


if __name__ == "__main__":
    test_calibration()
