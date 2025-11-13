"""
Скрипт для тестирования калибровки коэффициентов
"""

import os
import sys

from shield_ai.application.use_cases.calibrate_coefficients import CalibrateCoefficientsUseCase
from shield_ai.infrastructure.database.session import get_session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def test_calibration():
    with get_session() as session:
        use_case = CalibrateCoefficientsUseCase(session)
        results = use_case.execute_all()
        print("Калибровка завершена:", len(results), "товаров")
        for product_name, coeffs in results.items():
            print(
                f"  {product_name}: a={coeffs['a']:.4f}, b={coeffs['b']:.4f}, c={coeffs['c']:.4f}, статус={coeffs['status']}"
            )


if __name__ == "__main__":
    test_calibration()
