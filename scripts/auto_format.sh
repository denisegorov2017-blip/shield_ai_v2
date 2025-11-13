#!/bin/bash

# Скрипт для автоматического форматирования и исправления ошибок качества кода.
# Использует инструменты из poetry-окружения.

# 1. Сортировка импортов с помощью isort
echo "Running isort..."
poetry run isort .

# 2. Форматирование кода с помощью black
echo "Running black..."
poetry run black .

# 3. Автоматическое исправление ошибок с помощью ruff
echo "Running ruff check --fix..."
poetry run ruff check --fix .

echo "Auto-formatting complete."