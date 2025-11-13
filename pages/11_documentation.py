import streamlit as st

st.header("ℹ️ О системе")

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
