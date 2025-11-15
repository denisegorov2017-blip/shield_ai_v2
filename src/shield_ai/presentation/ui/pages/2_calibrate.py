"""
Streamlit страница: Калибровка коэффициентов
"""

from typing import (
    List,
    Tuple,
)

import pandas as pd
import plotly.express as px
import streamlit as st

from src.shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from src.shield_ai.application.use_cases.forecast_shrinkage import (
    ForecastShrinkageUseCase,
)
from src.shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from src.shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)
from src.shield_ai.infrastructure.logging_config import (
    get_logger,
)

# Настройка логирования
logger = get_logger(__name__)


def display_header() -> None:
    """Отображает заголовок страницы и инструкции."""
    st.header("📊 Калибровка коэффициентов усушки")

    st.info(
        """
**Шаг 2**: Система рассчитает индивидуальные коэффициенты для каждого товара.

**Метод**: Наименьших квадратов
**Модель**: Порционная (максимальная точность)
**Формула**: Усушка = M₀ × [a × (1 - e^(-b×t)) + c]
"""
    )


def check_session_state() -> Tuple[List[BatchMovement], List[BatchBalance]]:
    """Проверяет наличие данных в сессионном состоянии и возвращает их."""
    if "movements" not in st.session_state or "balances" not in st.session_state:
        st.warning(
            "⚠️ Данные отсутствуют. Пожалуйста, загрузите и распарсите Excel-файл на странице 'Парсинг Excel'."
        )
        st.stop()

    # Получаем данные из сессионного состояния
    movements: List[BatchMovement] = st.session_state.get("movements", [])
    balances: List[BatchBalance] = st.session_state.get("balances", [])

    if not movements or not balances:
        st.warning(
            "⚠️ Недостаточно данных для расчета. Пожалуйста, проверьте загруженный файл."
        )
        st.stop()

    st.success(
        f"✅ Загружено {len(movements)} записей движений и {len(balances)} записей остатков"
    )
    return movements, balances


def execute_calculation(
    calculation_type: str, movements: List[BatchMovement], balances: List[BatchBalance]
) -> List[ShrinkageCalculation]:
    """Выполняет расчет в зависимости от выбранного типа."""
    if calculation_type == "Калибровка коэффициентов":
        use_case = CalibrateCoefficientsUseCase()
        results = use_case.execute(movements, balances)
    else:
        use_case = ForecastShrinkageUseCase()
        results = use_case.execute(movements, balances)

    return results


def display_results(results: List[ShrinkageCalculation]) -> None:
    """Отображает результаты расчета."""
    if not results:
        st.warning("⚠️ Расчет не дал результатов. Проверьте данные и настройки.")
    else:
        st.success(f"✅ Рассчитано {len(results)} записей!")

        # Преобразуем результаты в DataFrame для отображения
        results_data = [
            {
                "Номенклатура": result.nomenclature,
                "Рассчитанная усушка": result.calculated_shrinkage,
                "Фактический остаток": result.actual_balance,
                "Отклонение": result.deviation,
            }
            for result in results
        ]

        df_results = pd.DataFrame(results_data)

        # Отображаем таблицу результатов
        st.subheader("Таблица результатов:")
        st.dataframe(df_results)

        # График рассчитанной усушки
        st.subheader("График рассчитанной усушки по номенклатурам:")
        fig1 = px.bar(
            df_results,
            x="Номенклатура",
            y="Рассчитанная усушка",
            title="Рассчитанная усушка по номенклатурам",
            labels={"Рассчитанная усушка": "Усушка", "Номенклатура": "Номенклатура"},
        )
        st.plotly_chart(fig1, use_container_width=True)

        # График отклонений
        st.subheader("График отклонений:")
        fig2 = px.bar(
            df_results,
            x="Номенклатура",
            y="Отклонение",
            title="Отклонение рассчитанной усушки от фактических данных",
            labels={"Отклонение": "Отклонение", "Номенклатура": "Номенклатура"},
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Дополнительная информация
        st.subheader("Детализация:")
        for result in results[:5]:  # Показываем первые 5 результатов
            with st.expander(f"Детали для {result.nomenclature}"):
                st.write(f"**Рассчитанная усушка**: {result.calculated_shrinkage}")
                st.write(f"**Фактический остаток**: {result.actual_balance}")
                st.write(f"**Отклонение**: {result.deviation}")

        logger.info(
            f"Расчет усушки завершен успешно. Обработано {len(results)} записей."
        )


def main():
    """Основная функция страницы калибровки."""
    display_header()

    # Проверяем наличие данных в сессионном состоянии
    movements, balances = check_session_state()

    # Выбор типа расчета
    calculation_type_input = st.radio(
        "Выберите тип расчета:",
        options=["Калибровка коэффициентов", "Прогноз усушки"],
        index=0,
    )

    # Проверяем, что значение выбрано
    if calculation_type_input is None:
        st.warning("⚠️ Пожалуйста, выберите тип расчета.")
        st.stop()

    calculation_type: str = calculation_type_input

    # Кнопка запуска расчета
    if st.button("Запустить расчет", type="primary"):
        with st.spinner("Выполняется расчет..."):
            try:
                # Выполняем расчет в зависимости от типа
                results = execute_calculation(calculation_type, movements, balances)

                # Отображаем результаты
                display_results(results)

            except Exception as e:
                error_msg = f"❌ Ошибка при выполнении расчета: {str(e)}"
                st.error(error_msg)
                logger.error(error_msg, exc_info=True)


if __name__ == "__main__":
    main()
