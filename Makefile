# Makefile for Shield AI v2.0

.PHONY: help install run test test-cov lint format mypy pyright pylint pre-commit bandit safety dependency-check ci complexity-check docs-build

help:
	@echo "🛡️ Shield AI - Команды разработки"
	@echo "=================================="
	@echo "make install    - Установка зависимостей"
	@echo "make run        - Запуск Streamlit UI"
	@echo "make init-db    - Инициализация БД"
	@echo "make test       - Запуск тестов"
	@echo "make test-cov   - Запуск тестов с отчетом о покрытии"
	@echo "make lint       - Линтинг (ruff)"
	@echo "make pylint     - Проверка стиля кода (pylint)"
	@echo "make format     - Форматирование (black+isort)"
	@echo "make mypy       - Проверка типов (mypy)"
	@echo "make pyright    - Проверка типов (pyright)"
	@echo "make pre-commit - Запуск pre-commit хуков"
	@echo "make bandit     - Сканирование безопасности"
	@echo "make safety     - Проверка уязвимостей в зависимостях"
	@echo "make dependency-check - Проверка актуальности зависимостей"
	@echo "make docs-build - Генерация документации (Sphinx)"
	@echo "make ci         - Полный CI пайплайн"
	@echo "make complexity-check - Анализ сложности кода (radon)"

install:
	poetry install

run:
	bash ./scripts/link_pages.sh
	poetry run streamlit run main.py

init-db:
	poetry run python -c "from shield_ai.infrastructure.database import init_db; init_db()"

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ -v --cov=src/ --cov-report=html --cov-report=term

test-unit:
	poetry run pytest tests/unit/ -v

test-integration:
	poetry run pytest tests/integration/ -v

test-validation:
	poetry run pytest tests/validation/ -v

lint:
	poetry run ruff check src/ tests/

pylint:
	poetry run pylint src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

mypy:
	poetry run mypy src/

pyright:
	poetry run pyright

pre-commit:
	poetry run pre-commit run --all-files

bandit:
	poetry run bandit -r src/

safety:
	poetry run safety check

dependency-check:
	poetry run pip-audit

ci: format lint pylint mypy pyright pre-commit bandit safety dependency-check complexity-check test-cov docs-build
	@echo "✅ CI пройден!"

complexity-check:
	poetry run radon cc src/ -s -a -n 10 && poetry run radon mi src/ -s

docs-build:
	poetry run sphinx-build -b html docs/ docs/_build
