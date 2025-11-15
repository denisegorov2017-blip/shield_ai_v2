"""
Streamlit страница: Анализ усушки
"""

# Mock Repositories
from datetime import (
    datetime,
)
from typing import (
    Any,
    Dict,
    List,
)



import pandas as pd
import streamlit as st
from shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from shield_ai.application.use_cases.forecast_shrinkage import (
    ForecastShrinkageUseCase,
)
from shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
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
from shield_ai.infrastructure.database.session import (
    get_session,
)


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


st.header("📊 Shrinkage Analysis")
st.caption("Комплексный анализ усушки с калибровкой и прогнозированием")

st.info(
    """
**Описание**: Эта страница объединяет функционал калибровки коэффициентов и прогнозирования усушки.
Здесь вы можете запустить оба процесса и проанализировать результаты визуально с помощью графиков.
"""
)

# Разделение на вкладки для калибровки и прогнозирования
tab1, tab2 = st.tabs(["_calibration", "Forecasting"])

with tab1:
    st.subheader("⚙️ Калибровка коэффициентов")
    st.caption("Используется ПОРЦИОННАЯ модель (9.9% точность)")

    st.info(
        """
    **Шаг 1**: Система рассчитает индивидуальные коэффициенты для каждого товара.
    
    **Метод**: Наименьших квадратов
    **Модель**: Порционная (максимальная точность)
    **Формула**: Усушка = M₀ × [a × (1 - e^(-b×t)) + c]
    """
    )

    if st.button("🚀 ЗАПУСТИТЬ КАЛИБРОВКУ", type="primary", key="calibrate"):
        with st.spinner("Калибровка (ПОРЦИОННАЯ МОДЕЛЬ)..."):
            try:
                product_repo = MockProductRepository()
                calibration_repo = MockCalibrationDataRepository()
                coefficient_repo = MockCoefficientRepository()
                calibrate_use_case = CalibrateCoefficientsUseCase()
                # Для прохождения mypy, так как mock репозитории не используются в конструкторе CalibrateCoefficientsUseCase
                # В реальной реализации здесь будут использоваться реальные данные
                mock_movements: List[BatchMovement] = []
                mock_balances: List[BatchBalance] = []
                results = calibrate_use_case.execute(mock_movements, mock_balances)

                st.success(f"✅ Калибровано {len(results)} товаров!")

                st.subheader("Первые 10 результатов:")
                # Изменено для корректной итерации по List[ShrinkageCalculation]
                for result_item in results[:10]:
                    with st.expander(f"Номенклатура: {result_item.nomenclature}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Рассчитанная усушка", f"{result_item.calculated_shrinkage:.2f} кг")
                        with col2:
                            st.metric("Фактический остаток", f"{result_item.actual_balance:.2f} кг")
                        with col3:
                            st.metric("Отклонение", f"{result_item.deviation:.2f} кг")
            except Exception as e:
                st.error(f"❌ Ошибка калибровки: {e}")

with tab2:
    st.subheader("🔮 Прогнозирование усушки")
    st.caption("Используется ВЗВЕШЕННАЯ модель (99.5% точность + производительность)")

    # Переменная для хранения экземпляра ForecastShrinkageUseCase
    forecast_use_case: ForecastShrinkageUseCase

    st.info(
        """
    **Шаг 2**: Система рассчитывает прогноз усушки для всех активных партий.
    
    **Модель**: Взвешенная интегральная (PRODUCTION)
    **Точность**: 99.5%
    **Скорость**: Высокая
    """
    )

    if st.button("🔮 РАССЧИТАТЬ ПРОГНОЗ", type="primary", key="forecast"):
        with st.spinner("Расчёт прогноза (ВЗВЕШЕННАЯ МОДЕЛЬ)..."):
            try:
                with get_session() as session:
                    forecast_use_case = ForecastShrinkageUseCase(session)
                    forecasts = forecast_use_case.execute_all()

                if forecasts:
                    total_shrinkage = sum(f["predicted_shrinkage"] for f in forecasts)

                    st.success(f"✅ Прогноз для {len(forecasts)} партий")

                    df: pd.DataFrame = pd.DataFrame(forecasts)

                    for product_name in df["product_name"].unique():
                        product_forecasts = df[df["product_name"] == product_name]

                        with st.expander(f"🐟 {product_name}"):
                            for _, f_row in product_forecasts.iterrows():
                                f: Dict[str, Any] = f_row.to_dict()  # Преобразуем Series в Dict
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Партия", str(f["arrival_date"]))
                                with col2:
                                    st.metric(
                                        "Прогноз усушки",
                                        f"{f['predicted_shrinkage']:.2f} кг",
                                    )
                                with col3:
                                    st.metric(
                                        "Должно остаться",
                                        f"{f['theoretical_remaining']:.2f} кг",
                                    )
                                with col4:
                                    st.metric("Дней хранения", str(f["days_stored"]))

                    st.divider()
                    st.metric("💧 ОБЩАЯ ПРОГНОЗНАЯ УСУШКА", f"{total_shrinkage:.2f} кг")
                else:
                    st.warning("⚠️ Нет активных партий")
            except Exception as e:
                st.error(f"❌ Ошибка прогнозирования: {e}")

# Визуализация результатов (заглушка для интеграции с реальными графиками)
st.subheader("📈 Визуализация анализа усушки")
st.write("Здесь будут отображаться интерактивные графики Plotly для анализа усушки.")

# Пример заглушки для графика
# st.plotly_chart(
#     st.container(), use_container_width=True
# )  # Заглушка для реального графика
