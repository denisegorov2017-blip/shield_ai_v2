# Makefile for Shield AI v2.0

.PHONY: help install run test lint format ci

help:
	@echo "🛡️ Shield AI - Команды разработки"
	@echo "=================================="
	@echo "make install   - Установка зависимостей"
	@echo "make run       - Запуск Streamlit UI"
	@echo "make init-db   - Инициализация БД"
	@echo "make test      - Запуск тестов"
	@echo "make lint      - Линтинг (ruff)"
	@echo "make format    - Форматирование (black+isort)"
	@echo "make mypy      - Проверка типов"
	@echo "make ci        - Полный CI пайплайн"

install:
	poetry install

run:
	bash ./scripts/link_pages.sh
	poetry run streamlit run main.py

init-db:
	poetry run python -c "from shield_ai.infrastructure.database import init_db; init_db()"

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

mypy:
	poetry run mypy src/

ci: format lint mypy test
	@echo "✅ CI пройден!"
