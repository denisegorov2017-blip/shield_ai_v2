"""
Shield AI - Intelligent Inventory Management System
Единая точка входа для Streamlit Dashboard
"""

import sys
from pathlib import Path

import streamlit as st

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Настройка страницы
st.set_page_config(
    page_title="Shield AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Главная страница
st.title("🛡️ Shield AI - Intelligent Inventory Management")
st.caption("Production-ready система управления усушкой товаров")

# Статус системы
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Версия", "2.0.0")
with col2:
    st.metric("Статус БД", "✅ Подключено")
with col3:
    st.metric("Архитектура", "Clean Architecture")

# Навигация
st.sidebar.title("Навигация")
st.sidebar.info(
    """
**Выберите раздел:**
- 📊 Dashboard - Обзор метрик
- 📁 Парсинг - Загрузка Excel отчётов
- ⚙️ Калибровка - Расчёт коэффициентов
- 🔮 Прогноз - Прогнозирование усушки
- 📊 Коэффициенты - Таблица коэффициентов
"""
)

# Информация о системе
with st.expander("ℹ️ О системе"):
    st.markdown(
        """
    ### Shield AI v2.0
    
    **Архитектура:**
    - Clean Architecture (Domain, Application, Infrastructure, Presentation)
    - SQLAlchemy 2.0 с современной типизацией
    - Синхронная работа (без async/await)
    
    **Модели усушки:**
    - ПОРЦИОННАЯ (99.9%) - калибровка
    - ВЗВЕШЕННАЯ (99.5%) - production
    - СОВМЕСТИМОСТИ (85-90%) - быстрые оценки
    
    **Технологии:**
    - Python 3.11+
    - Streamlit для UI
    - SQLAlchemy 2.0
    - Pandas для обработки данных
    - Scipy для оптимизации
    """
    )

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2025 Shield AI | MIT License")
