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

st.sidebar.page_link(
    "pages/0_project_metrics.py", label="Dashboard - Обзор метрик", icon="📊"
)
st.sidebar.page_link("pages/1_parse.py", label="Парсинг", icon="📁")
st.sidebar.page_link("pages/2_calibrate.py", label="Калибровка", icon="⚙️")
st.sidebar.page_link("pages/3_forecast.py", label="Прогноз", icon="🔮")
st.sidebar.page_link("pages/4_coefficients.py", label="Коэффициенты", icon="📊")
st.sidebar.page_link("pages/11_documentation.py", label="О системе", icon="ℹ️")

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2025 Shield AI | MIT License")
