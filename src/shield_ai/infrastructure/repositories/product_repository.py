"""
Репозиторий для работы с товарами (Product) через SQLAlchemy
"""

from typing import (
    List,
)

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)

from shield_ai.domain.entities.product import (
    Product,
)
from shield_ai.domain.repositories import (
    ProductRepository,
)
from shield_ai.infrastructure.database.models import (
    ProductModel,
)


class SQLAlchemyProductRepository(ProductRepository):
    """
    Реализация ProductRepository с использованием SQLAlchemy
    """

    def __init__(self, session: Session):
        """
        Инициализация репозитория

        Args:
            session: SQLAlchemy сессия для работы с базой данных
        """
        self.session = session

    def get_all(self) -> List[Product]:
        """
        Получить все товары из базы данных

        Returns:
            Список доменных сущностей Product
        """
        # Выполняем запрос к базе данных для получения всех записей ProductModel
        stmt = select(ProductModel)
        product_models = self.session.scalars(stmt).all()

        # Преобразуем каждую запись ProductModel в доменную сущность Product
        products = []
        for model in product_models:
            product = Product(
                id=model.id,
                name=model.name,
                group_name=model.group_name,
                created_at=model.created_at,
            )
            products.append(product)

        return products
