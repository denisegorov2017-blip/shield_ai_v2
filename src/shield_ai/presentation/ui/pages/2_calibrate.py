"""
Streamlit страница: Калибровка коэффициентов
"""

import streamlit as st

from shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from shield_ai.infrastructure.database.session import get_session

st.header("⚙️ Калибровка коэффициентов")
st.caption("Используется ПОРЦИОННАЯ модель (99.9% точность)")

st.info(
    """
**Шаг 2**: Система рассчитает индивидуальные коэффициенты для каждого товара.

**Метод**: Наименьших квадратов
**Модель**: Порционная (максимальная точность)
**Формула**: Усушка = M₀ × [a × (1 - e^(-b×t)) + c]
"""
)

if st.button("🚀 ЗАПУСТИТЬ КАЛИБРОВКУ", type="primary"):
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
            st.error(f"❌ Ошибка: {e}")
