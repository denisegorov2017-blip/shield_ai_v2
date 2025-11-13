"""
Use Case: Прогнозирование усушки
Использует ВЗВЕШЕННУЮ модель (99.5% точность)
"""

from datetime import date, datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from shield_ai.domain.shrinkage.strategies import WeightedStrategy
from shield_ai.infrastructure.database.models import (
    BatchModel,
    SaleModel,
    ShrinkageCoefficientModel,
)


class ForecastShrinkageUseCase:
    """
    Use Case: Прогнозирование усушки

    Модель: Взвешенная (99.5%) - PRODUCTION
    """

    def __init__(self, session: Session):
        self.session = session
        self.strategy = WeightedStrategy()

    def execute_all(self) -> List[Dict[str, Any]]:
        """Прогноз для всех активных партий"""
        stmt = select(BatchModel).where(BatchModel.remaining_qty > 0)
        batches = self.session.scalars(stmt).all()

        forecasts = []

        for batch in batches:
            coeffs = self._get_coefficients(batch.product_id)

            # Получаем продажи по дням
            sales_stmt = select(SaleModel).where(SaleModel.batch_id == batch.id)
            sales = self.session.scalars(sales_stmt).all()

            daily_sales: Dict[date, float] = {}
            for sale in sales:
                date_key = sale.sale_date.date()
                if date_key in daily_sales:
                    daily_sales[date_key] += sale.quantity
                else:
                    daily_sales[date_key] = sale.quantity

            batch_data = {
                "initial_mass": batch.initial_qty,
                "arrival_date": batch.arrival_datetime,
                "end_date": datetime.now(),
                "daily_sales": daily_sales,
            }

            predicted_shrinkage = self.strategy.calculate(batch_data, coeffs)
            sold = batch.initial_qty - batch.remaining_qty
            theoretical_remaining = batch.initial_qty - sold - predicted_shrinkage

            forecasts.append(
                {
                    "product_name": batch.product.name if batch.product else "Unknown",
                    "group_name": (
                        batch.product.group_name if batch.product else "Unknown"
                    ),
                    "arrival_date": batch.arrival_date,
                    "days_stored": (datetime.now() - batch.arrival_datetime).days,
                    "initial_qty": batch.initial_qty,
                    "sold_qty": sold,
                    "remaining_qty": batch.remaining_qty,
                    "predicted_shrinkage": predicted_shrinkage,
                    "theoretical_remaining": theoretical_remaining,
                    "coefficients": coeffs,
                }
            )

        return forecasts

    def _get_coefficients(self, product_id: int) -> Dict[str, Any]:
        """Получает коэффициенты"""
        stmt = select(ShrinkageCoefficientModel).where(
            ShrinkageCoefficientModel.product_id == product_id
        )
        coeff = self.session.scalars(stmt).first()

        if coeff:
            return {"a": coeff.a, "b": coeff.b, "c": coeff.c, "status": coeff.status}
        return {"a": 0.05, "b": 0.1, "c": 0.01, "status": "стандартные"}
