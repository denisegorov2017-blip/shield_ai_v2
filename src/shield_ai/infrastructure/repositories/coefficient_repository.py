"""
Репозиторий для работы с коэффициентами усушки (ShrinkageCoefficient) через SQLAlchemy
"""

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)

from shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCoefficient,
)
from shield_ai.domain.repositories import (
    CoefficientRepository,
)
from shield_ai.infrastructure.database.models import (
    ShrinkageCoefficientModel,
)


class SQLAlchemyCoefficientRepository(CoefficientRepository):
    """
    Реализация CoefficientRepository с использованием SQLAlchemy
    """

    def __init__(self, session: Session):
        """
        Инициализация репозитория

        Args:
            session: SQLAlchemy сессия для работы с базой данных
        """
        self.session = session

    def save(self, coeffs: ShrinkageCoefficient) -> None:
        """
        Сохраняет или обновляет коэффициенты усушки для товара в базе данных

        Args:
            coeffs: Доменная сущность ShrinkageCoefficient с коэффициентами
        """
        # Ищем существующую запись по product_id
        stmt = select(ShrinkageCoefficientModel).where(
            ShrinkageCoefficientModel.product_id == coeffs.product_id
        )
        existing_coeff = self.session.scalar(stmt)

        if existing_coeff:
            # Если запись найдена, обновляем её поля
            existing_coeff.a = coeffs.a
            existing_coeff.b = coeffs.b
            existing_coeff.c = coeffs.c
            existing_coeff.rmse = coeffs.rmse
            existing_coeff.data_points = coeffs.data_points
            existing_coeff.status = coeffs.status.value
            # Обновляем дату калибровки
            from datetime import (
                datetime,
            )

            existing_coeff.calibration_date = datetime.now()
        else:
            # Если запись не найдена, создаем новую
            new_coeff = ShrinkageCoefficientModel(
                product_id=coeffs.product_id,
                a=coeffs.a,
                b=coeffs.b,
                c=coeffs.c,
                rmse=coeffs.rmse,
                data_points=coeffs.data_points,
                status=coeffs.status.value,
            )
            self.session.add(new_coeff)

        # Сохраняем изменения в базе данных
        self.session.commit()
