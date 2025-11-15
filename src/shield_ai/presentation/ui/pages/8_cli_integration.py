"""Streamlit страница: Интеграция с CLI.

Этот модуль предоставляет интерфейс для выполнения команд командной строки
внутри Streamlit-приложения. Он использует subprocess для выполнения команд
с ограничениями безопасности.
"""

import shlex
import subprocess  # nosec
from typing import (
    Tuple,
)

import streamlit as st


def run_cli_command(command: str) -> Tuple[str, str]:
    """
    Выполняет команду CLI и возвращает stdout и stderr.

    Args:
        command: Команда для выполнения

    Returns:
        Кортеж из (stdout, stderr)
    """
    try:
        # Разбор команды с учетом кавычек и пробелов
        parsed_command = shlex.split(command)

        # Проверка, что команда не является потенциально опасной
        dangerous_commands = ["rm", "mv", "dd", "kill", "reboot", "shutdown"]
        if any(cmd in parsed_command for cmd in dangerous_commands):
            return (
                "",
                f"Ошибка: Команда содержит запрещенные элементы: {dangerous_commands}",
            )

        # Запускаем процесс с переданной командой
        result = subprocess.run(  # nosec
            parsed_command,
            capture_output=True,
            text=True,
            timeout=30,  # Таймаут 30 секунд
            check=True,
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Команда превысила таймаут в 30 секунд"
    except Exception as e:
        return "", f"Ошибка выполнения команды: {str(e)}"


def main():
    """Основная функция страницы интеграции с CLI."""
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
