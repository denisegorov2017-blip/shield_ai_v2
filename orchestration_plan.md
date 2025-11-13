# План для Оркестратора: Исправление ошибок качества кода

## Objective (Цель)

Автоматически и вручную исправить все ошибки качества кода, выявленные
`isort`, `black`, `ruff` и `mypy`, и убедиться, что код соответствует
стандартам проекта.

## Context (Контекст)

- **Проект:** Shield AI v2.0
- **Файлы с ошибками:** `main.py`,
  `src/shield_ai/domain/shrinkage/strategies.py`,
  `src/shield_ai/application/use_cases/forecast_shrinkage.py`,
  `src/shield_ai/application/use_cases/calibrate_coefficients.py`,
  `pages/3_forecast.py`.
- **План исправления:** [`code_quality_plan.md`](code_quality_plan.md)

## Acceptance Criteria (Критерии приемки)

1. Все файлы отформатированы с помощью `isort` и `black`.
1. Все автоматически исправляемые ошибки `ruff` устранены.
1. Все ошибки `mypy` исправлены.
1. Код успешно проходит все проверки (`isort`, `black`, `ruff`, `mypy`) без ошибок.

## Expected Artifact (Ожидаемый артефакт)

- JSON-отчет со статусом `success`.
- Артефакты, содержащие измененные файлы.

## Constraints (Ограничения)

- Не изменять публичные API.
- Не добавлять новые зависимости без необходимости.

## План выполнения

1. **Делегировать `Code`:**

   - **Objective:** Создать и выполнить скрипт `scripts/auto_format.sh` для
     автоматического исправления `isort`, `black` и `ruff`.
   - **Context:** Содержимое скрипта находится в [`code_quality_plan.md`](code_quality_plan.md).
   - **Acceptance Criteria:** Скрипт выполнен, большинство ошибок
     форматирования и импортов исправлены.
   - **Expected Artifact:** JSON-отчет со статусом `success` и списком
     измененных файлов.

1. **Делегировать `Code`:**

   - **Objective:** Установить `pandas-stubs` и `scipy-stubs` для исправления
     ошибок `mypy`.
   - **Context:** Ошибки `mypy` указывают на отсутствие заглушек типов.
   - **Acceptance Criteria:** Зависимости `pandas-stubs` и `scipy-stubs`
     добавлены в `pyproject.toml` и установлены.
   - **Expected Artifact:** JSON-отчет со статусом `success`.

1. **Делегировать `Code`:**

   - **Objective:** Исправить оставшиеся ошибки `mypy` в файлах
     `strategies.py`, `forecast_shrinkage.py`,
     `calibrate_coefficients.py`.
   - **Context:** Ошибки `Missing type parameters for generic type "Dict"`,
     `Returning Any from function declared to return "float"`,
     `Cannot instantiate abstract class "ShrinkageStrategy"`,
     `Need type annotation for "daily_sales"`.
   - **Acceptance Criteria:** Все ошибки `mypy` исправлены.
   - **Expected Artifact:** JSON-отчет со статусом `success` и списком
     измененных файлов.

1. **Делегировать `Code`:**

   - **Objective:** Запустить все проверки (`isort`, `black`, `ruff`, `mypy`)
     и убедиться, что ошибок нет.
   - **Context:** Финальная проверка после всех исправлений.
   - **Acceptance Criteria:** Все проверки проходят без ошибок.
   - **Expected Artifact:** JSON-отчет со статусом `success` и выводом
     консоли без ошибок.
