import streamlit as st


def main():
    st.title("Project Metrics")

    # MyPy Progress
    st.header("MyPy Progress")
    st.text_input("MyPy Coverage", value="85%", disabled=True)
    st.progress(0.85)

    # CI Status
    st.header("CI Status")
    st.text_input("Build Status", value="Success", disabled=True)
    st.text_input("Last Run", value="2025-11-13 14:30:00", disabled=True)


if __name__ == "__main__":
    main()