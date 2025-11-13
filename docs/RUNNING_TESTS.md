# 🧪 Запуск тестов и проверка функциональности

## Общая информация

Shield AI v2.0 включает в себя несколько ключевых компонентов, которые можно протестировать отдельно:

1. **Калибровка коэффициентов** - расчет индивидуальных коэффициентов усушки для товаров
1. **Прогнозирование усушки** - предсказание потерь для активных партий
1. **Стратегии усушки** - три различных модели расчета (Порционная, Взвешенная, Совместимости)

## Подготовка окружения

### Инициализация базы данных

```bash
# С помощью скрипта
python -c "from src.shield_ai.infrastructure.database.base import init_db; init_db()"

# Или через Makefile
make init-db
```

### Добавление тестовых данных

```python
# test_data.py
"""
Скрипт для добавления тестовых данных в базу данных
"""
from datetime import datetime, timedelta
from src.shield_ai.infrastructure.database.session import get_session
from src.shield_ai.infrastructure.database.models import ProductModel, BatchModel, SaleModel, InventoryModel
import random

def add_test_data():
    with get_session() as session:
        # Создаем тестовые товары
        products = []
        for i in range(1, 4):
            product = ProductModel(
                name=f"Тестовый товар {i}",
                group_name=f"Группа {i}",
                created_at=datetime.now()
            )
            session.add(product)
            products.append(product)
        
        session.commit()
        
        # Создаем тестовые партии
        for i, product in enumerate(products):
            batch = BatchModel(
                product_id=product.id,
                arrival_date=(datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%d.%m.%Y'),
                arrival_datetime=datetime.now() - timedelta(days=random.randint(30, 180)),
                initial_qty=random.uniform(10, 500),
                remaining_qty=random.uniform(50, 300)
            )
            session.add(batch)
        
        session.commit()
        
        # Создаем тестовые продажи
        batches = session.query(BatchModel).all()
        for batch in batches:
            for day in range(0, random.randint(5, 15)):
                sale_date = batch.arrival_datetime + timedelta(days=day)
                if sale_date < datetime.now():
                    sale = SaleModel(
                        batch_id=batch.id,
                        sale_date=sale_date,
                        quantity=random.uniform(1, 10),
                        document_name=f"Документ-{batch.id}-{day}"
                    )
                    session.add(sale)
        
        session.commit()
        
        # Создаем тестовые инвентаризации
        for product in products:
            inventory = InventoryModel(
                product_id=product.id,
                inventory_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                expected_qty=random.uniform(50, 200),
                actual_qty=random.uniform(45, 190),
                shrinkage=random.uniform(1, 10)
            )
            session.add(inventory)
        
        session.commit()
        print(f"✅ Добавлено: {len(products)} товаров, {len(batches)} партий, {session.query(SaleModel).count()} продаж, {session.query(InventoryModel).count()} инвентаризаций")

if __name__ == "__main__":
    add_test_data()
```

## Тестирование калибровки коэффициентов

```bash
# Установка PYTHONPATH для корректного импорта
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
python -c "
from src.shield_ai.application.use_cases.calibrate_coefficients import CalibrateCoefficientsUseCase
from src.shield_ai.infrastructure.database.session import get_session

with get_session() as session:
    use_case = CalibrateCoefficientsUseCase(session)
    results = use_case.execute_all()
    print('Калибровка завершена:', len(results), 'товаров')
    for product_name, coeffs in results.items():
        print(f'  {product_name}: a={coeffs[\"a\"]:.4f}, b={coeffs[\"b\"]:.4f}, c={coeffs[\"c\"]:.4f}, статус={coeffs[\"status\"]}')
"
```

## Тестирование прогнозирования усушки

```bash
# Установка PYTHONPATH для корректного импорта
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
python -c "
from src.shield_ai.application.use_cases.forecast_shrinkage import ForecastShrinkageUseCase
from src.shield_ai.infrastructure.database.session import get_session

with get_session() as session:
    use_case = ForecastShrinkageUseCase(session)
    forecasts = use_case.execute_all()
    print('Прогнозирование завершено:', len(forecasts), 'записей')
    for forecast in forecasts:
        print(f'  {forecast[\"product_name\"]}: прогноз усушки = {forecast[\"predicted_shrinkage\"]:.2f} кг, '
              f'останется = {forecast[\"theoretical_remaining\"]:.2f} кг, '
              f'дней хранения = {forecast[\"days_stored\"]}')
"
```

## Стратегии усушки

В системе реализованы три стратегии расчета усушки:

1. **ПОРЦИОННАЯ МОДЕЛЬ** (99.9% точность) - используется для калибровки

   - Каждая продажа рассматривается как отдельная порция
   - Формула: `Усушка_порции = m * [a * (1 - e^(-b*t)) + c]`

1. **ВЗВЕШЕННАЯ ИНТЕГРАЛЬНАЯ МОДЕЛЬ** (99.5% точность) - используется для production прогнозов

   - Усушка рассчитывается дискретно по дням с учётом остатка
   - Подходит для реальных расчетов

1. **МОДЕЛЬ СОВМЕСТИМОСТИ** (85-90% точность) - для быстрых оценок

   - Усушка для всей партии за всё время без учёта продаж

## Проверка через UI

После запуска Streamlit приложения можно проверить функциональность через веб-интерфейс:

```bash
streamlit run main.py
```

Доступные разделы:

- 📊 Dashboard - Обзор метрик
- 📁 Парсинг - Загрузка Excel отчётов
- ⚙️ Калибровка - Расчёт коэффициентов
- 🔮 Прогноз - Прогнозирование усушки
- 📊 Коэффициенты - Таблица коэффициентов

## Тестовые скрипты

Для удобства тестирования можно использовать следующие скрипты:

### test_calibration.py

```python
"""
Скрипт для тестирования калибровки коэффициентов
"""
from src.shield_ai.application.use_cases.calibrate_coefficients import CalibrateCoefficientsUseCase
from src.shield_ai.infrastructure.database.session import get_session

def test_calibration():
    with get_session() as session:
        use_case = CalibrateCoefficientsUseCase(session)
        results = use_case.execute_all()
        print('Калибровка завершена:', len(results), 'товаров')
        for product_name, coeffs in results.items():
            print(f'  {product_name}: a={coeffs["a"]:.4f}, b={coeffs["b"]:.4f}, c={coeffs["c"]:.4f}, статус={coeffs["status"]}')

if __name__ == "__main__":
    test_calibration()
```

### test_forecast.py

```python
"""
Скрипт для тестирования прогнозирования усушки
"""
from src.shield_ai.application.use_cases.forecast_shrinkage import ForecastShrinkageUseCase
from src.shield_ai.infrastructure.database.session import get_session

def test_forecast():
    with get_session() as session:
        use_case = ForecastShrinkageUseCase(session)
        forecasts = use_case.execute_all()
        print('Прогнозирование завершено:', len(forecasts), 'записей')
        for forecast in forecasts:
            print(f'  {forecast["product_name"]}: прогноз усушки = {forecast["predicted_shrinkage"]:.2f} кг, '
                  f'останется = {forecast["theoretical_remaining"]:.2f} кг, '
                  f'дней хранения = {forecast["days_stored"]}')

if __name__ == "__main__":
    test_forecast()
```

Запуск тестовых скриптов:

```bash
PYTHONPATH="${PYTHONPATH}:${PWD}/src" python test_calibration.py
PYTHONPATH="${PYTHONPATH}:${PWD}/src" python test_forecast.py
```
