"""
Streamlit страница: Парсинг Excel
"""

import tempfile
from typing import (
    List,
    Optional,
    Tuple,
)
import pandas as pd
import streamlit as st
from shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from shield_ai.infrastructure.logging_config import (
    get_logger,
)
from shield_ai.infrastructure.parsers.hierarchical_excel_parser import (
    HierarchicalExcelParser,
)
from shield_ai.infrastructure.parsers.dto import FlatRecord

# Настройка логирования
logger = get_logger(__name__)


def display_header() -> None:
    """Отображает заголовок страницы и инструкции."""
    st.header("📁 Парсинг Excel-отчётов из 1C")

    # Отображение информации об ошибках и версии схемы
    col1, col2, col3 = st.columns(3)
    with col1:
        if "error_logs" in st.session_state and st.session_state["error_logs"]:
            total_errors = len(st.session_state["error_logs"])
            has_critical_errors = any(log["type"] == "error" for log in st.session_state["error_logs"])
            error_status = f"🔴 Ошибок: {total_errors}" if has_critical_errors else f"🟡 Логов: {total_errors}"
            st.metric("Ошибки/предупреждения", error_status)
        else:
            st.metric("Ошибки/предупреждения", "✅ Нет")
    with col2:
        if "error_logs" in st.session_state and st.session_state["error_logs"]:
            has_critical_errors = any(log["type"] == "error" for log in st.session_state["error_logs"])
            critical_status = "🔴 Есть критичные ошибки" if has_critical_errors else "✅ Нет критичных ошибок"
            st.metric("Критичные ошибки", critical_status)
        else:
            st.metric("Критичные ошибки", "✅ Нет")
    with col3:
        st.metric("Версия схемы FlatRecord", "1.0")

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


def parse_excel_file(file_path: str) -> Tuple[List[BatchMovement], List[BatchBalance], List[dict]]:
    """Парсит Excel файл и возвращает объекты BatchMovement, BatchBalance и логи ошибок."""
    parser = HierarchicalExcelParser()
    flat_records, error_logs = parser.parse(file_path)
    
    # Преобразуем FlatRecord в BatchMovement и BatchBalance
    movements = []
    balances = []
    
    for record in flat_records:
        # Создаем BatchMovement для прихода и расхода
        if record.qty_in > 0:
            movements.append(BatchMovement(
                nomenclature=record.product,
                date=record.doc_date,
                movement_type="Приход",
                quantity=float(record.qty_in),
                warehouse=record.warehouse
            ))
        if record.qty_out > 0:
            movements.append(BatchMovement(
                nomenclature=record.product,
                date=record.doc_date,
                movement_type="Расход",
                quantity=float(record.qty_out),
                warehouse=record.warehouse
            ))
        
        # Создаем BatchBalance для остатков
        balances.append(BatchBalance(
            nomenclature=record.product,
            date=record.batch_date,
            balance=float(record.qty_end),
            warehouse=record.warehouse,
            batch=record.batch_code
        ))
    
    return movements, balances, error_logs


def display_parsing_results(
    movements: List[BatchMovement], balances: List[BatchBalance], error_logs: List[dict]
) -> None:
    """Отображает результаты парсинга и логи ошибок."""
    st.success(f"✅ Файл успешно распарсен.")

    # Отображение результатов парсинга
    st.write(f"**Количество записей BatchMovement:** {len(movements)}")
    st.write(f"**Количество записей BatchBalance:** {len(balances)}")
    st.write(f"**Количество ошибок/предупреждений:** {len(error_logs)}")

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

    # Отображение логов ошибок
    if error_logs:
        st.subheader("📋 Логи ошибок и предупреждений")
        
        # Фильтрация логов
        col1, col2 = st.columns(2)
        with col1:
            log_types = ["Все", "error", "warning"]
            selected_type = st.selectbox("Тип лога", log_types, key="log_type")
        with col2:
            search_term = st.text_input("Поиск по сообщению", key="log_search")
        
        # Фильтруем логи
        filtered_logs = error_logs
        if selected_type != "Все":
            filtered_logs = [log for log in filtered_logs if log['type'] == selected_type]
        if search_term:
            search_term = search_term.lower()
            filtered_logs = [log for log in filtered_logs if search_term in log['message'].lower()]
        
        if filtered_logs:
            # Создаем DataFrame для отображения
            logs_df = pd.DataFrame(filtered_logs)
            
            # Переименовываем колонки для лучшего отображения
            display_df = logs_df.rename(columns={
                'row': 'Строка',
                'type': 'Тип',
                'message': 'Сообщение',
                'data': 'Данные'
            })
            
            # Показываем таблицу с логами
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Кнопки для экспорта логов
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Выгрузить логи ошибок (CSV)",
                    data=logs_df.to_csv(index=False, encoding='utf-8'),
                    file_name="error_logs.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="📥 Выгрузить логи ошибок (JSON)",
                    data=logs_df.to_json(orient='records', force_ascii=False),
                    file_name="error_logs.json",
                    mime="application/json"
                )
        else:
            st.info("❌ Нет логов, соответствующих фильтрам")
    else:
        st.info("✅ Нет ошибок или предупреждений при обработке файла")


def display_batch_results(batch_results: List[dict]) -> None:
    """Отображает сводные результаты пакетной обработки."""
    st.subheader("📊 Сводка по всем файлам")
    
    # Подготовка данных для таблицы
    summary_data = []
    for result in batch_results:
        summary_data.append({
            "Файл": result["filename"],
            "Статус": "✅ Успешно" if result["success"] else "❌ Ошибка",
            "Записей BatchMovement": len(result["movements"]),
            "Записей BatchBalance": len(result["balances"]),
            "Ошибок": len(result["error_logs"]),
        })
    
    # Отображение сводной таблицы
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Отображение деталей для каждого файла
    for i, result in enumerate(batch_results):
        with st.expander(f"📄 {result['filename']} - Детали", expanded=False):
            if result["success"]:
                st.write(f"**Статус:** ✅ Успешно")
                st.write(f"**Количество записей BatchMovement:** {len(result['movements'])}")
                st.write(f"**Количество записей BatchBalance:** {len(result['balances'])}")
                st.write(f"**Количество ошибок/предупреждений:** {len(result['error_logs'])}")
                
                # Показываем примеры первых нескольких записей
                if result['movements']:
                    st.write(f"**Примеры первых {min(5, len(result['movements']))} записей BatchMovement:**")
                    movements_data = [
                        {
                            "Номенклатура": m.nomenclature,
                            "Дата": m.date,
                            "Тип движения": m.movement_type,
                            "Количество": m.quantity,
                            "Склад": m.warehouse,
                        }
                        for m in result['movements'][:5]
                    ]
                    st.dataframe(movements_data)
                
                if result['balances']:
                    st.write(f"**Примеры первых {min(5, len(result['balances']))} записей BatchBalance:**")
                    balances_data = [
                        {
                            "Номенклатура": b.nomenclature,
                            "Дата": b.date,
                            "Баланс": b.balance,
                            "Склад": b.warehouse,
                            "Партия": b.batch,
                        }
                        for b in result['balances'][:5]
                    ]
                    st.dataframe(balances_data)
                
                # Отображение логов ошибок
                if result['error_logs']:
                    st.subheader("📋 Логи ошибок и предупреждений")
                    
                    # Фильтрация логов
                    col1, col2 = st.columns(2)
                    with col1:
                        log_types = ["Все", "error", "warning"]
                        selected_type = st.selectbox("Тип лога", log_types, key=f"log_type_{i}")
                    with col2:
                        search_term = st.text_input("Поиск по сообщению", key=f"log_search_{i}")
                    
                    # Фильтруем логи
                    filtered_logs = result['error_logs']
                    if selected_type != "Все":
                        filtered_logs = [log for log in filtered_logs if log['type'] == selected_type]
                    if search_term:
                        search_term = search_term.lower()
                        filtered_logs = [log for log in filtered_logs if search_term in log['message'].lower()]
                    
                    if filtered_logs:
                        # Создаем DataFrame для отображения
                        logs_df = pd.DataFrame(filtered_logs)
                        
                        # Переименовываем колонки для лучшего отображения
                        display_df = logs_df.rename(columns={
                            'row': 'Строка',
                            'type': 'Тип',
                            'message': 'Сообщение',
                            'data': 'Данные'
                        })
                        
                        # Показываем таблицу с логами
                        st.dataframe(display_df, use_container_width=True, height=400)
                        
                        # Кнопки для экспорта логов
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Выгрузить логи ошибок (CSV)",
                                data=logs_df.to_csv(index=False, encoding='utf-8'),
                                file_name=f"{result['filename']}_error_logs.csv",
                                mime="text/csv"
                            )
                        with col2:
                            st.download_button(
                                label="📥 Выгрузить логи ошибок (JSON)",
                                data=logs_df.to_json(orient='records', force_ascii=False),
                                file_name=f"{result['filename']}_error_logs.json",
                                mime="application/json"
                            )
                    else:
                        st.info("❌ Нет логов, соответствующих фильтрам")
                else:
                    st.info("✅ Нет ошибок или предупреждений при обработке файла")
            else:
                st.write(f"**Статус:** ❌ Ошибка")
                st.write(f"**Сообщение об ошибке:** {result['error_message']}")


def display_aggregated_summary(batch_results: List[dict]) -> None:
    """Отображает агрегированный summary по batch-загрузке."""
    st.subheader("📈 Агрегированный summary по batch-загрузке")
    
    # Подсчет агрегированных метрик
    total_files = len(batch_results)
    successful_files = len([r for r in batch_results if r["success"]])
    failed_files = total_files - successful_files
    total_movements = sum(len(r["movements"]) for r in batch_results if r["success"])
    total_balances = sum(len(r["balances"]) for r in batch_results if r["success"])
    total_error_logs = sum(len(r["error_logs"]) for r in batch_results)
    total_flat_records = sum(len(r.get("flat_records", [])) for r in batch_results if r["success"])
    
    # Подсчет ошибок по типам
    error_counts = {"error": 0, "warning": 0}
    for result in batch_results:
        for log in result["error_logs"]:
            if log["type"] in error_counts:
                error_counts[log["type"]] += 1
    
    # Отображение агрегированных метрик
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Обработано файлов", total_files)
    with col2:
        st.metric("Файлов с ошибками", failed_files)
    with col3:
        st.metric("Всего записей FlatRecord", total_flat_records)
    with col4:
        st.metric("Всего ошибок", total_error_logs)
    with col5:
        st.metric("Всего предупреждений", error_counts["warning"])
    
    # Дополнительная статистика
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Записей BatchMovement", total_movements)
    with col2:
        st.metric("Записей BatchBalance", total_balances)
    with col3:
        success_rate = (successful_files / total_files * 10) if total_files > 0 else 0
        st.metric("Процент успеха", f"{success_rate:.1f}%")
    
    # Сводка по типам ошибок
    if error_counts["error"] > 0 or error_counts["warning"] > 0:
        st.subheader("⚠️ Сводка по типам ошибок")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Критические ошибки", error_counts["error"])
        with col2:
            st.metric("Предупреждения", error_counts["warning"])
    else:
        st.success("✅ Нет ошибок или предупреждений в batch-загрузке")


def display_visualization(flat_records: List[FlatRecord]) -> None:
    """Отображает визуализацию данных из FlatRecord."""
    if not flat_records:
        st.warning("⚠️ Нет данных для визуализации")
        return

    st.subheader("📈 Визуализация данных")
    
    # Преобразуем FlatRecord в DataFrame для визуализации
    df = pd.DataFrame([record.dict() for record in flat_records])
    
    # Статистика по основным показателям
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Всего записей", len(df))
    with col2:
        st.metric("Уникальных складов", df['warehouse'].nunique())
    with col3:
        st.metric("Уникальных товаров", df['product'].nunique())
    with col4:
        st.metric("Уникальных партий", df['batch_code'].nunique())
    with col5:
        st.metric("Типов документов", df['doc_type'].nunique())
    
    # График распределения видов движений
    st.subheader("📊 Распределение видов движений")
    doc_type_counts = df['doc_type'].value_counts()
    st.bar_chart(doc_type_counts)
    
    # Таблица с распределением видов движений
    st.write("**Таблица распределения видов движений:**")
    doc_type_df = pd.DataFrame({
        'Тип документа': doc_type_counts.index,
        'Количество': doc_type_counts.values
    })
    st.dataframe(doc_type_df, use_container_width=True)
    
    # График изменения остатков по времени для выбранного товара/склада
    st.subheader("📈 Изменение остатков по времени")
    
    # Выбор товара и склада
    col1, col2 = st.columns(2)
    with col1:
        selected_product = st.selectbox("Выберите товар", options=df['product'].unique())
    with col2:
        selected_warehouse = st.selectbox("Выберите склад", options=df['warehouse'].unique())
    
    # Фильтрация данных
    filtered_df = df[
        (df['product'] == selected_product) & 
        (df['warehouse'] == selected_warehouse)
    ].copy()
    
    if not filtered_df.empty:
        # Сортировка по дате
        filtered_df = filtered_df.sort_values('batch_date')
        
        # Создание графика
        chart_data = pd.DataFrame({
            'Дата': filtered_df['batch_date'],
            'Остаток': filtered_df['qty_end']
        })
        
        st.line_chart(data=chart_data.set_index('Дата'))
        
        # Таблица с данными
        st.write("**Данные по остаткам:**")
        balance_table = filtered_df[['batch_date', 'batch_code', 'qty_begin', 'qty_in', 'qty_out', 'qty_end']].copy()
        balance_table = balance_table.rename(columns={
            'batch_date': 'Дата',
            'batch_code': 'Партия',
            'qty_begin': 'Нач. остаток',
            'qty_in': 'Приход',
            'qty_out': 'Расход',
            'qty_end': 'Кон. остаток'
        })
        st.dataframe(balance_table, use_container_width=True)
    else:
        st.info("❌ Нет данных для выбранной комбинации товара и склада")
    
    # Визуализация данных по усушке (если доступны)
    st.subheader("📉 Анализ усушки")
    
    # В текущей реализации усушка не рассчитывается, но мы можем показать
    # потенциальные данные, если они будут доступны в будущем
    st.info("ℹ️ В текущей версии данные по усушке не рассчитываются автоматически. Ниже показаны потенциальные метрики, которые будут доступны после реализации расчета усушки.")
    
    # Показываем возможные метрики усушки
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Потенциальная усушка", "0.00 кг")
    with col2:
        st.metric("Макс. усушка", "0.00 кг")
    with col3:
        st.metric("Средняя усушка", "0.00 кг")
    
    # Заглушка для будущей визуализации усушки
    st.write("Здесь будет отображаться график усушки по партиям, когда функциональность будет реализована.")


def main():
    """Основная функция страницы парсинга."""
    display_header()

    # Обновленный загрузчик файлов для поддержки множественной загрузки
    uploaded_files = st.file_uploader(
        "Выбери Excel файлы", 
        type=["xlsx", "xls"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) == 1:
            # Обработка одного файла (старая логика)
            uploaded_file = uploaded_files[0]
            try:
                # Используем временный файл, так как парсер принимает путь к файлу
                tmp_path = create_temp_file(uploaded_file)

                # Парсим файл и получаем объекты BatchMovement, BatchBalance и логи ошибок
                movements, balances, error_logs = parse_excel_file(tmp_path)

                # Отображаем результаты парсинга
                display_parsing_results(movements, balances, error_logs)

                # Сохраняем результаты в сессионное состояние для использования на других страницах
                st.session_state["movements"] = movements
                st.session_state["balances"] = balances
                st.session_state["error_logs"] = error_logs

                # Также сохраняем FlatRecord для визуализации
                parser = HierarchicalExcelParser()
                flat_records, _ = parser.parse(tmp_path)
                st.session_state["flat_records"] = flat_records

            except Exception as e:
                error_msg = f"❌ Ошибка при обработке файла: {str(e)}"
                st.error(error_msg)
                logger.error(error_msg, exc_info=True)
        else:
            # Обработка нескольких файлов (новая логика batch upload)
            st.info(f"Обработка {len(uploaded_files)} файлов...")
            
            batch_results = []
            progress_bar = st.progress(0)
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    # Обновление прогресса
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    # Используем временный файл, так как парсер принимает путь к файлу
                    tmp_path = create_temp_file(uploaded_file)

                    # Парсим файл и получаем объекты BatchMovement, BatchBalance и логи ошибок
                    movements, balances, error_logs = parse_excel_file(tmp_path)
                    
                    # Получаем FlatRecord для подсчета общего количества записей
                    parser = HierarchicalExcelParser()
                    flat_records, _ = parser.parse(tmp_path)
                    
                    # Сохраняем результаты для этого файла
                    batch_results.append({
                        "filename": uploaded_file.name,
                        "success": True,
                        "movements": movements,
                        "balances": balances,
                        "error_logs": error_logs,
                        "flat_records": flat_records  # Добавляем FlatRecord для подсчета общего количества
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Ошибка при обработке файла {uploaded_file.name}: {str(e)}"
                    st.error(error_msg)
                    logger.error(error_msg, exc_info=True)
                    
                    # Сохраняем информацию об ошибке
                    batch_results.append({
                        "filename": uploaded_file.name,
                        "success": False,
                        "movements": [],
                        "balances": [],
                        "error_logs": [],
                        "error_message": str(e),
                        "flat_records": []  # Добавляем пустой список для согласованности
                    })
            
            # Отображение сводных результатов
            display_batch_results(batch_results)
            
            # Отображение агрегированного summary
            display_aggregated_summary(batch_results)
            
            # Сохранение результатов последнего успешного файла в сессионное состояние
            # для использования на других страницах (если есть хотя бы один успешный файл)
            successful_results = [r for r in batch_results if r["success"]]
            if successful_results:
                last_successful = successful_results[-1]
                st.session_state["movements"] = last_successful["movements"]
                st.session_state["balances"] = last_successful["balances"]
                st.session_state["error_logs"] = last_successful["error_logs"]
                
                # Также сохраняем FlatRecord для визуализации
                parser = HierarchicalExcelParser()
                last_successful_file = next(f for f in uploaded_files if f.name == last_successful["filename"])
                tmp_path = create_temp_file(last_successful_file)
                flat_records, _ = parser.parse(tmp_path)
                st.session_state["flat_records"] = flat_records

        # Отображение визуализации, если данные доступны
        if "flat_records" in st.session_state and st.session_state["flat_records"]:
            display_visualization(st.session_state["flat_records"])
    else:
        st.warning("⚠️ Загрузи Excel файл(ы) для начала работы")


if __name__ == "__main__":
    main()
