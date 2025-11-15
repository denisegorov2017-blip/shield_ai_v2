"""
Streamlit страница: Парсинг Excel
"""

import tempfile
from typing import (
    List,
    Optional,
    Tuple,
)

import streamlit as st
from shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from shield_ai.infrastructure.logging_config import (
    get_logger,
)
from shield_ai.infrastructure.parsers.inventory_parser import (
    InventoryParser,
)

# Настройка логирования
logger = get_logger(__name__)


def display_header() -> None:
    """Отображает заголовок страницы и инструкции."""
    st.header("📁 Парсинг Excel-отчётов из 1C")

    st.info(
        """
**Шаг 1**: Загрузи Excel файл с партиями товаров.
Система автоматически распарсит файл и создаст объекты BatchMovement и BatchBalance.
"""
    )

    # Заголовок "Excel Upload"
    st.subheader("Excel Upload")


def create_temp_file(uploaded_file) -> str:
    """Создает временный файл из загруженного файла."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def parse_excel_file(file_path: str) -> Tuple[List[BatchMovement], List[BatchBalance]]:
    """Парсит Excel файл и возвращает объекты BatchMovement и BatchBalance."""
    parser = InventoryParser()
    return parser.parse_excel(file_path)


def display_parsing_results(
    movements: List[BatchMovement], balances: List[BatchBalance]
) -> None:
    """Отображает результаты парсинга."""
    st.success(f"✅ Файл успешно распарсен.")

    # Отображение результатов парсинга
    st.write(f"**Количество записей BatchMovement:** {len(movements)}")
    st.write(f"**Количество записей BatchBalance:** {len(balances)}")

    # Показываем примеры первых нескольких записей
    if movements:
        st.write(f"**Примеры первых {min(5, len(movements))} записей BatchMovement:**")
        movements_data = [
            {
                "Номенклатура": m.nomenclature,
                "Дата": m.date,
                "Тип движения": m.movement_type,
                "Количество": m.quantity,
                "Склад": m.warehouse,
            }
            for m in movements[:5]
        ]
        st.dataframe(movements_data)

    if balances:
        st.write(f"**Примеры первых {min(5, len(balances))} записей BatchBalance:**")
        balances_data = [
            {
                "Номенклатура": b.nomenclature,
                "Дата": b.date,
                "Баланс": b.balance,
                "Склад": b.warehouse,
                "Партия": b.batch,
            }
            for b in balances[:5]
        ]
        st.dataframe(balances_data)


def main():
    """Основная функция страницы парсинга."""
    display_header()

    uploaded_file = st.file_uploader("Выбери Excel файл", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Используем временный файл, так как парсер принимает путь к файлу
            tmp_path = create_temp_file(uploaded_file)

            # Парсим файл и получаем объекты BatchMovement и BatchBalance
            movements, balances = parse_excel_file(tmp_path)

            # Отображаем результаты парсинга
            display_parsing_results(movements, balances)

            # Сохраняем результаты в сессионное состояние для использования на других страницах
            st.session_state["movements"] = movements
            st.session_state["balances"] = balances

        except Exception as e:
            error_msg = f"❌ Ошибка при обработке файла: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg, exc_info=True)
    else:
        st.warning("⚠️ Загрузи Excel файл для начала работы")


if __name__ == "__main__":
    main()
