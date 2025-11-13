"""
Скрипт для тестирования прогнозирования усушки
"""

from src.shield_ai.application.use_cases.forecast_shrinkage import ForecastShrinkageUseCase
from src.shield_ai.infrastructure.database.session import get_session


def test_forecast():
    with get_session() as session:
        use_case = ForecastShrinkageUseCase(session)
        forecasts = use_case.execute_all()
        print("Прогнозирование завершено:", len(forecasts), "записей")
        for forecast in forecasts:
            print(
                f'  {forecast["product_name"]}: прогноз усушки = {forecast["predicted_shrinkage"]:.2f} кг, '
                f'останется = {forecast["theoretical_remaining"]:.2f} кг, '
                f'дней хранения = {forecast["days_stored"]}'
            )


if __name__ == "__main__":
    test_forecast()
