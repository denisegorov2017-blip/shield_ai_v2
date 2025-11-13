"""
Streamlit страница: Парсинг Excel
"""

import tempfile

import pandas as pd
import streamlit as st

from src.shield_ai.infrastructure.parsers.inventory_parser import InventoryParser

st.header("📁 Парсинг Excel-отчётов из 1C")

st.info(
    """
**Шаг 1**: Загрузи Excel файл с партиями товаров.
Система автоматически распарсит файл и сохранит данные в БД.
"""
)

# Заголовок "Excel Upload"
st.subheader("Excel Upload")

uploaded_file = st.file_uploader("Выбери Excel файл", type=["xlsx", "xls"])

# Добавляем выбор типа парсера
parser_type = st.selectbox(
    "Выберите тип парсера",
    ["Стандартный (pandas)", "Парсер остатков (Inventory)"],
    key="parser_type_selector",
)

if uploaded_file:
    try:
        if parser_type == "Стандартный (pandas)":
            # Чтение Excel файла стандартным способом
            df = pd.read_excel(uploaded_file)

            st.success(f"✅ Файл загружен: {uploaded_file.name}")

            # Отображение первых нескольких строк данных
            st.write(f"**Просмотр первых {min(5, len(df))} строк данных:**")
            st.dataframe(df.head())

            # Отображение основной информации о файле
            st.write(f"**Размеры файла:** {df.shape[0]} строк x {df.shape[1]} столбцов")
            st.write(f"**Названия столбцов:** {', '.join(df.columns.tolist())}")

            if st.button("🚀 ЗАГРУЗИТЬ И РАСПАРСИТЬ", type="primary"):
                with st.spinner("Парсинг файла..."):
                    st.info("🛠️ Функционал парсинга будет добавлен в следующем релизе")
        else:  # Парсер остатков (Inventory)
            parser = InventoryParser()
            # Обрати внимание, что `parse_file` принимает путь, а не файловый объект.
            # Тебе нужно будет временно сохранить uploaded_file, чтобы передать путь.
            # Например, так:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            result = parser.parse_file(tmp_path)

            if result.get("error"):
                st.error(f"Ошибка парсинга: {result['error']}")
                st.stop()

            # Преобразование результата в DataFrame для отображения
            all_products = []
            for section in result.get("sections", []):
                for product in section.get("products", []):
                    for batch in product.get("batches", []):
                        all_products.append(
                            {
                                "Группа": section.get("name"),
                                "Товар": product.get("name"),
                                "Партия": batch.get("batch_code"),
                                "Нач. остаток": batch["qty"]["begin"],
                                "Приход": batch["qty"]["in"],
                                "Расход": batch["qty"]["out"],
                                "Кон. остаток": batch["qty"]["end"],
                            }
                        )
            df = pd.DataFrame(all_products)

            st.success(f"✅ Файл загружен: {uploaded_file.name}")

            # Отображение первых нескольких строк данных
            st.write(f"**Просмотр первых {min(5, len(df))} строк данных:**")
            st.dataframe(df.head())

            # Отображение основной информации о файле
            st.write(f"**Размеры файла:** {df.shape[0]} строк x {df.shape[1]} столбцов")
            st.write(f"**Названия столбцов:** {', '.join(df.columns.tolist())}")

            st.subheader("Метаданные парсинга")
            st.json(result.get("meta", {}))

            if st.button("🚀 ЗАГРУЗИТЬ И РАСПАРСИТЬ", type="primary"):
                with st.spinner("Парсинг файла..."):
                    st.info("🛠️ Функционал парсинга будет добавлен в следующем релизе")
    except Exception as e:
        st.error(f"❌ Ошибка при обработке файла: {str(e)}")
else:
    st.warning("⚠️ Загрузи Excel файл для начала работы")
