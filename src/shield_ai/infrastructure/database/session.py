"""
Управление сессиями SQLAlchemy 2.0 (синхронное)
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from .base import engine

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,  # SQLAlchemy 2.0 стиль
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Контекстный менеджер для сессий

    Использование:
        with get_session() as session:
            products = session.query(ProductModel).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """
    Получение сессии (для использования вне контекстного менеджера)

    ВАЖНО: Нужно вручную закрывать через session.close()
    """
    return SessionLocal()
