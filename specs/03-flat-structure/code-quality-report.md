# Отчет о качестве кода

## Обзор

Этот отчет содержит результаты статической проверки качества кода с использованием `pylint` и `mypy` для директории `src/shield_ai`. Проверка проводилась после завершения рефакторинга для выявления потенциальных ошибок, несоответствий стилю и проблем с типами.

## Результаты Pylint

### Общая оценка
Код получил оценку 8.98/10.

### Найденные проблемы
```
************* Module shield_ai.domain.entities.batch
src/shield_ai/domain/entities/batch.py:32:0: C0304: Final newline missing (missing-final-newline)
src/shield_ai/domain/entities/batch.py:11:0: R0902: Too many instance attributes (9/7) (too-many-instance-attributes)
************* Module shield_ai.domain.entities
src/shield_ai/domain/entities/__init__.py:5:0: E0611: No name 'Batch' in module 'shield_ai.domain.entities.batch' (no-name-in-module)
src/shield_ai/domain/entities/__init__.py:7:0: E0611: No name 'CoefficientStatus' in module 'shield_ai.domain.entities.shrinkage_profile' (no-name-in-module)
src/shield_ai/domain/entities/__init__.py:7:0: E0611: No name 'ShrinkageProfile' in module 'shield_ai.domain.entities.shrinkage_profile' (no-name-in-module)
************* Module shield_ai.domain.entities.shrinkage_profile
src/shield_ai/domain/entities/shrinkage_profile.py:21:0: C0304: Final newline missing (missing-final-newline)
src/shield_ai/domain/entities/shrinkage_profile.py:10:0: R0902: Too many instance attributes (10/7) (too-many-instance-attributes)
************* Module shield_ai.application.use_cases.calibrate_coefficients
src/shield_ai/application/use_cases/calibrate_coefficients.py:157:0: C0304: Final newline missing (missing-final-newline)
src/shield_ai/application/use_cases/calibrate_coefficients.py:17:0: E0611: No name 'ShrinkageCoefficient' in module 'shield_ai.domain.entities.shrinkage_profile' (no-name-in-module)
************* Module shield_ai.infrastructure.parsers.inventory_parser
src/shield_ai/infrastructure/parsers/inventory_parser.py:64:0: C0304: Final newline missing (missing-final-newline)
```

## Результаты MyPy

### Общая информация
Проверка завершена с ошибками (exit code 1). Найдено 11 ошибок в 3 файлах.

### Найденные проблемы
```
src/shield_ai/infrastructure/parsers/inventory_parser.py:12: error: Library stubs not installed for "pandas"  [import-untyped]
src/shield_ai/infrastructure/parsers/inventory_parser.py:12: note: Hint: "python3 -m pip install pandas-stubs"
src/shield_ai/infrastructure/parsers/inventory_parser.py:52: error: Function is missing a return type annotation  [no-untyped-def]
src/shield_ai/infrastructure/parsers/inventory_parser.py:52: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
src/shield_ai/domain/entities/__init__.py:5: error: Module "shield_ai.domain.entities.batch" has no attribute "Batch"  [attr-defined]
src/shield_ai/domain/entities/__init__.py:7: error: Module "shield_ai.domain.entities.shrinkage_profile" has no attribute "CoefficientStatus"  [attr-defined]
src/shield_ai/domain/entities/__init__.py:7: error: Module "shield_ai.domain.entities.shrinkage_profile" has no attribute "ShrinkageProfile"  [attr-defined]
src/shield_ai/application/use_cases/calibrate_coefficients.py:14: error: Library stubs not installed for "scipy.optimize"  [import-untyped]
src/shield_ai/application/use_cases/calibrate_coefficients.py:14: note: Hint: "python3 -m pip install scipy-stubs"
src/shield_ai/application/use_cases/calibrate_coefficients.py:14: note: (or run "mypy --install-types" to install all missing stub packages)
src/shield_ai/application/use_cases/calibrate_coefficients.py:14: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
src/shield_ai/application/use_cases/calibrate_coefficients.py:17: error: Module "shield_ai.domain.entities.shrinkage_profile" has no attribute "ShrinkageCoefficient"  [attr-defined]
src/shield_ai/application/use_cases/calibrate_coefficients.py:72: error: Argument 1 to "get_for_product" of "CalibrationDataRepository" has incompatible type "int | None"; expected "int"  [arg-type]
src/shield_ai/application/use_cases/calibrate_coefficients.py:75: error: Argument 1 to "_save_coefficients" of "CalibrateCoefficientsUseCase" has incompatible type "int | None"; expected "int" [arg-type]
src/shield_ai/application/use_cases/calibrate_coefficients.py:111: error: Returning Any from function declared to return "float"  [no-any-return]
```

## Краткое резюме

Оба анализатора (`pylint` и `mypy`) выявили проблемы в коде:

1.  **PyLint**:
    *   Отсутствие символа новой строки в конце некоторых файлов.
    *   Наличие слишком большого количества атрибутов в классах `Batch` и `ShrinkageProfile`.
    *   Ошибки импорта: отсутствие атрибутов `Batch`, `CoefficientStatus`, `ShrinkageProfile`, `ShrinkageCoefficient` в соответствующих модулях. Это указывает на возможные проблемы с определением или импортом классов в модулях `__init__.py`.

2.  **MyPy**:
    *   Отсутствие установленных библиотечных заглушек для `pandas` и `scipy.optimize`. Рекомендуется установить `pandas-stubs` и `scipy-stubs`.
    *   Отсутствие аннотаций типов для аргументов и возвращаемого значения функции в `inventory_parser.py`.
    *   Ошибки импорта, аналогичные `pylint`: отсутствие атрибутов `Batch`, `CoefficientStatus`, `ShrinkageProfile`, `ShrinkageCoefficient`.
    *   Несовместимые типы аргументов: передача `int | None` вместо `int` в `calibrate_coefficients.py`.
    *   Функция, возвращающая `Any`, но объявленная как возвращающая `float`.

Эти проблемы указывают на необходимость доработки кода для улучшения его надежности, читаемости и соответствия стандартам типизации Python.