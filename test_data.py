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
                initial_qty=random.uniform(100, 500),
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