"""
Streamlit страница: Анализ усушки
"""

import pandas as pd
import streamlit as st

from shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from shield_ai.application.use_cases.forecast_shrinkage import ForecastShrinkageUseCase
from shield_ai.infrastructure.database.session import get_session

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
                with get_session() as session:
                    use_case = CalibrateCoefficientsUseCase(session)
                    results = use_case.execute_all()

                st.success(f"✅ Калибровано {len(results)} товаров!")

                st.subheader("Первые 10 результатов:")
                for product_name, coeffs in list(results.items())[:10]:
                    with st.expander(f"{product_name} ({coeffs['status']})"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("a (макс усушка)", f"{coeffs['a'] * 100:.2f}%")
                        with col2:
                            st.metric("b (скорость)", f"{coeffs['b']:.4f}")
                        with col3:
                            st.metric("c (постоянная)", f"{coeffs['c'] * 100:.2f}%")
                        with col4:
                            if coeffs["rmse"]:
                                st.metric("RMSE", f"{coeffs['rmse']:.3f} кг")
            except Exception as e:
                st.error(f"❌ Ошибка калибровки: {e}")

with tab2:
    st.subheader("🔮 Прогнозирование усушки")
    st.caption("Используется ВЗВЕШЕННАЯ модель (99.5% точность + производительность)")

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
                    use_case = ForecastShrinkageUseCase(session)
                    forecasts = use_case.execute_all()

                if forecasts:
                    total_shrinkage = sum(f["predicted_shrinkage"] for f in forecasts)

                    st.success(f"✅ Прогноз для {len(forecasts)} партий")

                    df = pd.DataFrame(forecasts)

                    for product_name in df["product_name"].unique():
                        product_forecasts = df[df["product_name"] == product_name]

                        with st.expander(f"🐟 {product_name}"):
                            for _, f in product_forecasts.iterrows():
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Партия", f["arrival_date"])
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
                                    st.metric("Дней хранения", f"{f['days_stored']}")

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
