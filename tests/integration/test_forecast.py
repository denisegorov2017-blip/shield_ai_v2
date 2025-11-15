"""
Скрипт для тестирования прогнозирования усушки
"""

import os
import sys

from shield_ai.application.use_cases.forecast_shrinkage import (
    ForecastShrinkageUseCase,
)
from shield_ai.infrastructure.database.session import (
    get_session,
)

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)


def test_forecast():
    with get_session() as session:
        use_case = ForecastShrinkageUseCase(session)
        forecasts = use_case.execute_all()
        print("Прогнозирование завершено:", len(forecasts), "записей")
        for forecast in forecasts:
            print(forecast)  # Выводим элементы списка как есть, так как структура может отличаться


if __name__ == "__main__":
    test_forecast()
