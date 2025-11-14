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

# Загрузка файла-справочника
groups_file = st.file_uploader("Загрузите файл-справочник групп (необязательно)", type=["xlsx", "xls"])

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
            # Обрати внимание, что `parse_file` принимает путь, а не файловый объект.
            # Тебе нужно будет временно сохранить uploaded_file, чтобы передать путь.
            # Например, так:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            # Обработка файла-справочника
            groups_file_path = None
            if groups_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as groups_tmp:
                    groups_tmp.write(groups_file.getbuffer())
                    groups_file_path = groups_tmp.name

            # Теперь выполнить парсинг
            parser = InventoryParser(groups_file=groups_file_path)
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

            # Отладочный вывод: количество строк, прочитанных из Excel
            st.info(f"📊 Найдено строк данных: {len(df)}")
            
            # Отладочный вывод: информация о том, какие данные искал парсер
            sections_count = len(result.get("sections", []))
            products_count = sum(len(section.get("products", [])) for section in result.get("sections", []))
            batches_count = sum(len(product.get("batches", [])) for section in result.get("sections", []) for product in section.get("products", []))
            stats = result.get("meta", {}).get("stats", {})
            total_docs = stats.get("total_docs", 0)
            batch_movements = stats.get("batch_movements", 0)
            st.info(
                f"🔍 Парсер нашел: {sections_count} групп, {products_count} товаров, {batches_count} партий, "
                f"{total_docs} документов, {batch_movements} движений партий."
            )
            
            # Отладочный вывод: первые 5 строк из загруженного Excel-файла для предварительного просмотра
            st.write(f"**Предварительный просмотр первых 5 строк:**")
            st.dataframe(df.head())

            st.success(f"✅ Файл загружен: {uploaded_file.name}")

            # Отображение первых нескольких строк данных
            st.write(f"**Просмотр первых {min(5, len(df))} строк данных:**")
            st.dataframe(df.head())

            # Отображение основной информации о файле
            st.write(f"**Размеры файла:** {df.shape[0]} строк x {df.shape[1]} столбцов")
            st.write(f"**Названия столбцов:** {', '.join(df.columns.tolist())}")

            # Проверяем наличие предупреждений в метаданных
            if "warnings" in result.get("meta", {}) and result["meta"]["warnings"]:
                with st.expander("⚠️ Предупреждения парсинга"):
                    for warning in result["meta"]["warnings"]:
                        st.warning(warning)

            # Новый блок диагностики
            with st.expander("📊 Статистика парсинга"):
                parsing_stats = result.get("meta", {}).get("stats", {})
                st.json(parsing_stats)
            
            with st.expander("🔍 Полный результат (JSON)"):
                st.json(result)

            if st.button("🚀 ЗАГРУЗИТЬ И РАСПАРСИТЬ", type="primary"):
                with st.spinner("Парсинг файла..."):
                    st.info("🛠️ Функционал парсинга будет добавлен в следующем релизе")
    except Exception as e:
        st.error(f"❌ Ошибка при обработке файла: {str(e)}")
else:
    st.warning("⚠️ Загрузи Excel файл для начала работы")
