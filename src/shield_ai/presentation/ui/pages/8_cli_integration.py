import subprocess
import sys
from io import StringIO

import streamlit as st


def run_cli_command(command: str) -> tuple[str, str]:
    """
    Выполняет команду CLI и возвращает stdout и stderr.

    Args:
        command: Команда для выполнения

    Returns:
        Кортеж из (stdout, stderr)
    """
    # Используем subprocess для выполнения команды
    try:
        # Запускаем процесс с переданной командой
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # Таймаут 30 секунд
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Команда превысила таймаут в 30 секунд"
    except Exception as e:
        return "", f"Ошибка выполнения команды: {str(e)}"


def main():
    st.title("CLI Integration")
    st.write("Выполнение команд командной строки в Streamlit приложении")

    # Текстовое поле для ввода команды
    command = st.text_input(
        "Введите команду CLI:",
        value="",
        help="Введите команду для выполнения в терминале",
    )

    # Кнопка для выполнения команды
    if st.button("Выполнить команду"):
        if command.strip():
            with st.spinner(f"Выполнение команды: {command}"):
                stdout, stderr = run_cli_command(command)

            # Отображение результата
            if stdout:
                st.subheader("Вывод команды (stdout):")
                st.code(stdout, language="bash")

            if stderr:
                st.subheader("Ошибки (stderr):")
                st.error(stderr)
        else:
            st.warning("Пожалуйста, введите команду для выполнения")


if __name__ == "__main__":
    main()
