# Отчет о полной проверке качества кода

## Результат выполнения команды `make all`

Команда `make all` была выполнена в терминале, но завершилась с ошибками.

## Вывод команды

```
poetry run black src/ tests/
reformatted /home/user909/shield_ai_v2/src/shield_ai/infrastructure/database/__init__.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/domain/entities/__init__.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/domain/entities/batch.py
reformatted /home/user909/shield_ai_v2/tests/integration/test_calibration.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/infrastructure/parsers/inventory_parser.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/presentation/ui/pages/1_parse.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/domain/entities/shrinkage_profile.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/presentation/ui/pages/2_calibrate.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/application/use_cases/calibrate_coefficients.py
reformatted /home/user909/shield_ai_v2/src/shield_ai/presentation/ui/pages/5_shrinkage_analysis.py

All done! ✨ 🍰 ✨
10 files reformatted, 25 files left unchanged.
poetry run isort src/ tests/
Fixing /home/user909/shield_ai_v2/src/shield_ai/domain/entities/__init__.py
Fixing /home/user909/shield_ai_v2/src/shield_ai/presentation/ui/pages/2_calibrate.py
Fixing /home/user909/shield_ai_v2/src/shield_ai/presentation/ui/pages/5_shrinkage_analysis.py
Fixing /home/user909/shield_ai_v2/src/shield_ai/application/use_cases/calibrate_coefficients.py
Fixing /home/user909/shield_ai_v2/src/shield_ai/infrastructure/database/__init__.py
Fixing /home/user909/shield_ai_v2/tests/integration/test_calibration.py
poetry run ruff check src/ tests/
src/shield_ai/application/use_cases/calibrate_coefficients.py:12:37: F401 [*] `typing.Optional` imported but unused
src/shield_ai/domain/entities/batch.py:7:20: F401 [*] `typing.Optional` imported but unused
src/shield_ai/presentation/ui/pages/1_parse.py:7:18: F401 [*] `pandas` imported but unused
Found 3 errors.
[*] 3 fixable with the `--fix` option.
make: *** [Makefile:74: lint] Error 1
```

## Заключение

Проверка не пройдена. Обнаружены ошибки линтинга в следующих файлах:
1. `src/shield_ai/application/use_cases/calibrate_coefficients.py` - неиспользуемый импорт `typing.Optional`
2. `src/shield_ai/domain/entities/batch.py` - неиспользуемый импорт `typing.Optional`
3. `src/shield_ai/presentation/ui/pages/1_parse.py` - неиспользуемый импорт `pandas`

Для исправления этих ошибок можно запустить `make fix` или `poetry run ruff check --fix src/ tests/`.