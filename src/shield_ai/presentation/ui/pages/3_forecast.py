"""
Streamlit страница: Прогноз усушки
"""

import streamlit as st

from shield_ai.application.use_cases.forecast_shrinkage import ForecastShrinkageUseCase
from shield_ai.infrastructure.database.session import get_session

st.header("🔮 Прогнозирование усушки")
st.caption("Используется ВЗВЕШЕННАЯ модель (99.5% точность + производительность)")

st.info(
    """
**Шаг 3**: Система рассчитывает прогноз усушки для всех активных партий.

**Модель**: Взвешенная интегральная (PRODUCTION)
**Точность**: 99.5%
**Скорость**: Высокая
"""
)

if st.button("🔮 РАССЧИТАТЬ ПРОГНОЗ", type="primary"):
    with st.spinner("Расчёт прогноза (ВЗВЕШЕННАЯ МОДЕЛЬ)..."):
        try:
            with get_session() as session:
                use_case = ForecastShrinkageUseCase(session)
                forecasts = use_case.execute_all()

            if forecasts:
                total_shrinkage = sum(f["predicted_shrinkage"] for f in forecasts)

                st.success(f"✅ Прогноз для {len(forecasts)} партий")

                import pandas as pd

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
            st.error(f"❌ Ошибка: {e}")
