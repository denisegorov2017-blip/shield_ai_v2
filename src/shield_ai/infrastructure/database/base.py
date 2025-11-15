"""
SQLAlchemy 2.0 base configuration
Синхронная работа (без async)
"""

import os

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ocean_shop.db")


# Базовый класс для моделей
class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей"""


# Engine (синхронный)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,  # True для отладки SQL  # SQLAlchemy 2.0 стиль
)


def init_db() -> None:
    """Создание всех таблиц"""
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")
