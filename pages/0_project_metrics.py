import streamlit as st

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