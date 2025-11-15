from typing import (
    Any,
    Dict,
    List,
)

from sqlalchemy.orm import (
    Session,
)

from shield_ai.domain.repositories import (
    CalibrationDataRepository,
)
from shield_ai.infrastructure.database.models import (
    BatchModel,
    SaleModel,
)


class SQLAlchemyCalibrationDataRepository(CalibrationDataRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_for_product(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Получает данные для калибровки для заданного продукта.

        :param product_id: ID продукта
        :return: Список словарей с данными о партиях, включая дату поступления,
                 список продаж и фактическую усушку
        """
        # Находим все завершенные партии (remaining_qty = 0) для продукта
        batches = (
            self.session.query(BatchModel)
            .filter(BatchModel.product_id == product_id, BatchModel.remaining_qty == 0)
            .all()
        )

        result = []
        for batch in batches:
            # Получаем все продажи для текущей партии
            sales = (
                self.session.query(SaleModel)
                .filter(SaleModel.batch_id == batch.id)
                .all()
            )

            # Формируем список продаж с датой и количеством
            sales_data = [
                {"date": sale.sale_date, "quantity": sale.quantity} for sale in sales
            ]

            # Рассчитываем фактическую усушку
            total_sold_qty = sum(sale.quantity for sale in sales)
            actual_shrinkage = batch.initial_qty - total_sold_qty

            # Формируем словарь с данными о партии
            batch_data = {
                "arrival_date": batch.arrival_date,
                "sales": sales_data,
                "actual_shrinkage": actual_shrinkage,
            }

            result.append(batch_data)

        return result
