# Задачи по реализации: Обработка внешних партий

**Ветка**: `002-external-batch-processing` | **Дата**: 2025-11-13 | **Спецификация**: [specs/002-external-batch-processing/spec.md](specs/002-external-batch-processing/spec.md)
**План**: [specs/002-external-batch-processing/plan.md](specs/002-external-batch-processing/plan.md)

## Задачи

- [ ] Модифицировать метод `_apply_fifo_expense` для создания external batch.
- [ ] Добавить подробный лог через `logger.info`/`logger.error` при создании партии.
- [ ] В итоговом отчёте добавить явное уведомление о таких партиях.
- [ ] В Markdown/JSON добавить визуальное выделение external batch (цвет/иконка/флаг).