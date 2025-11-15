# Makefile for Shield AI v2.0

.PHONY: help install run test test-cov lint format pyright pylint pre-commit bandit safety dependency-check ci complexity-check docs-build typecheck security coverage complexity all

help:
	@echo "🛡️ Shield AI - Команды разработки"
	@echo "=================================="
	@echo "make install    - Установка зависимостей"
	@echo "make run        - Запуск Streamlit UI"
	@echo "make init-db    - Инициализация БД"
	@echo "make test       - Запуск тестов (pytest)"
	@echo "make test-cov   - Запуск тестов с отчетом о покрытии"
	@echo "make lint       - Линтинг (ruff)"
	@echo "make pylint     - Проверка стиля кода (pylint)"
	@echo "make format     - Форматирование (black+isort)"
	@echo "make typecheck  - Проверка типов (pyright)"
	@echo "make pyright    - Проверка типов (pyright)"
	@echo "make pre-commit - Запуск pre-commit хуков"
	@echo "make bandit     - Сканирование безопасности"
	@echo "make safety     - Проверка уязвимостей в зависимостях"
	@echo "make dependency-check - Проверка актуальности зависимостей"
	@echo "make docs-build - Генерация документации (Sphinx)"
	@echo "make ci         - Полный CI пайплайн"
	@echo "make complexity-check - Анализ сложности кода (radon)"
	@echo "make security   - Проверка безопасности (bandit + pip-audit)"
	@echo "make coverage   - Отчет покрытия тестами (проверка >= 80%)"
	@echo "make complexity - Метрики сложности кода (radon)"
	@echo "make all        - Полная проверка перед коммитом (все команды + pre-commit hooks)"

install:
	poetry install

run:
	bash ./scripts/link_pages.sh
	poetry run streamlit run main.py

typecheck:
	poetry run pyright

security:
	poetry run bandit -r src/
	poetry run pip-audit

coverage:
	poetry run pytest tests/ -v --cov=src/shield_ai --cov-report=html --cov-report=xml --cov-report=term --cov-fail-under=80 -n auto

complexity:
	poetry run radon cc src/shield_ai -s -a -n 10 && poetry run radon mi src/shield_ai -s

all: format lint pyright security complexity test-cov docs-build
	@echo "✅ Все проверки пройдены!"

init-db:
	poetry run python -c "from shield_ai.infrastructure.database import init_db; init_db()"

migrate:
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "Initial migration"

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
	poetry run ruff check src/ tests/ --fix --exit-zero


pyright:
	poetry run pyright

pre-commit:
	poetry run pre-commit run --all-files

bandit:
	poetry run bandit -r src/
safety:
	poetry run safety check

pip-audit:
	poetry run pip-audit

dependency-check:
	poetry run pip-audit


ci: format lint pylint pyright pre-commit bandit safety dependency-check complexity-check test-cov docs-build
	@echo "✅ CI пройден!"

complexity-check:
	poetry run radon cc src/ -s -a -n 10 && poetry run radon mi src/ -s

docs-build:
	LANG=C.UTF-8 LC_ALL=C.UTF-8 poetry run sphinx-build -b html docs/ docs/_build
