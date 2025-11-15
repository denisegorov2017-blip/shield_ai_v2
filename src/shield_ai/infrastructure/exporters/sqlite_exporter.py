"""
Модуль реализации экспорта в формат SQLite.

Содержит реализацию экспортера, который преобразует список объектов
ShrinkageCalculation в таблицу SQLite и записывает в базу данных.
"""

from typing import (
    List,
)

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from ...domain.entities.shrinkage_profile import (
    ShrinkageCalculation,
)
from ..export_interfaces import (
    Exporter,
)
from ..logging_config import (
    get_logger,
)


def _create_orm_item(item: ShrinkageCalculation) -> "ShrinkageCalculationORM":
    """
    Создает ORM модель из объекта ShrinkageCalculation.

    Args:
        item: Объект ShrinkageCalculation

    Returns:
        ORM модель для сохранения в базе данных
    """
    return ShrinkageCalculationORM(
        nomenclature=item.nomenclature,
        calculated_shrinkage=item.calculated_shrinkage,
        actual_balance=item.actual_balance,
        deviation=item.deviation,
    )


class Base(DeclarativeBase):
    """Базовый класс для ORM моделей SQLAlchemy."""

    pass


class ShrinkageCalculationORM(Base):
    """ORM модель для хранения результатов расчёта усушки в SQLite."""

    __tablename__ = "shrinkage_calculations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nomenclature = Column(String(500), nullable=False)
    calculated_shrinkage = Column(Float, nullable=False)
    actual_balance = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)


class SQLiteExporter(Exporter):
    """
    Реализация экспорта данных ShrinkageCalculation в формат SQLite.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def export(self, data: List[ShrinkageCalculation], output_path: str) -> None:
        """
        Экспортирует список объектов ShrinkageCalculation в SQLite базу данных.

        Args:
            data: Список объектов ShrinkageCalculation для экспорта
            output_path: Путь к файлу базы данных SQLite, в который нужно экспортировать данные
        """
        self.logger.info(
            "Начало экспорта в SQLite", output_path=output_path, count=len(data)
        )

        # Создаем подключение к базе данных SQLite
        engine = create_engine(f"sqlite:///{output_path}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Очищаем таблицу перед вставкой новых данных
            session.query(ShrinkageCalculationORM).delete()

            # Преобразуем объекты ShrinkageCalculation в ORM модели
            orm_items = [_create_orm_item(item) for item in data]

            # Добавляем все элементы в сессию
            session.add_all(orm_items)

            # Сохраняем изменения в базе данных
            session.commit()
            self.logger.info(
                "Экспорт в SQLite завершен успешно", output_path=output_path
            )

        except Exception as e:
            session.rollback()
            self.logger.error("Ошибка при экспорте в SQLite", error=str(e))
            raise
        finally:
            session.close()
