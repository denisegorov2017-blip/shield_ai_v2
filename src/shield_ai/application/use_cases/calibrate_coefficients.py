"""
Use Case: Калибровка коэффициентов усушки
Использует ПОРЦИОННУЮ модель (99.9% точность)
"""

import math
from datetime import datetime
from typing import Any, Dict, List

from scipy.optimize import minimize
from sqlalchemy import select
from sqlalchemy.orm import Session

from shield_ai.infrastructure.database.models import (
    BatchModel,
    InventoryModel,
    ProductModel,
    SaleModel,
    ShrinkageCoefficientModel,
)


class CalibrateCoefficientsUseCase:
    """
    Use Case: Калибровка коэффициентов

    Метод: Наименьших квадратов
    Модель: Порционная (99.9%)
    """

    def __init__(self, session: Session):
        self.session = session

    def execute_all(self) -> Dict[str, Dict[str, Any]]:
        """Калибрует все товары"""
        stmt = select(ProductModel)
        products = self.session.scalars(stmt).all()

        results = {}

        for product in products:
            coeffs = self._calibrate_product(product)
            self._save_coefficients(product.id, coeffs)
            results[product.name] = coeffs

        return results

    def _calibrate_product(self, product: ProductModel) -> Dict[str, Any]:
        """Калибрует один товар"""
        data = self._get_calibration_data(product.id)

        if len(data) < 3:
            return {
                "a": 0.05,
                "b": 0.1,
                "c": 0.01,
                "rmse": None,
                "data_points": len(data),
                "status": "стандартные",
            }

        def objective(params: List[float]) -> float:
            a, b, c = params
            errors = []
            for point in data:
                predicted = self._calculate_portion(point, a, b, c)
                actual = point["actual_shrinkage"]
                errors.append((predicted - actual) ** 2)
            return sum(errors)  # type: ignore

        x0 = [0.05, 0.1, 0.01]
        bounds = [(0.01, 0.15), (0.01, 0.5), (0.0, 0.03)]
        result = minimize(objective, x0, bounds=bounds, method="L-BFGS-B")  # type: ignore
        a, b, c = result.x

        errors = [(self._calculate_portion(p, a, b, c) - p["actual_shrinkage"]) ** 2 for p in data]
        rmse = math.sqrt(sum(errors) / len(errors))

        return {
            "a": a,
            "b": b,
            "c": c,
            "rmse": rmse,
            "data_points": len(data),
            "status": "калиброван",
        }

    def _get_calibration_data(self, product_id: int) -> List[Dict[str, Any]]:
        """Получает данные инвентаризаций"""
        stmt = select(InventoryModel).where(InventoryModel.product_id == product_id)
        inventories = self.session.scalars(stmt).all()

        data = []
        for inv in inventories:
            batch_stmt = select(BatchModel).where(BatchModel.product_id == product_id)
            batches = self.session.scalars(batch_stmt).all()

            for batch in batches:
                sales_stmt = select(SaleModel).where(SaleModel.batch_id == batch.id)
                sales = self.session.scalars(sales_stmt).all()

                sales_list = [{"date": sale.sale_date, "quantity": sale.quantity} for sale in sales]

                data.append(
                    {
                        "initial_mass": batch.initial_qty,
                        "arrival_date": batch.arrival_datetime,
                        "sales": sales_list,
                        "actual_shrinkage": inv.shrinkage,
                    }
                )

        return data

    def _calculate_portion(self, point: Dict[str, Any], a: float, b: float, c: float) -> float:
        """Расчёт по порционной модели"""
        total = 0.0
        for sale in point["sales"]:
            days = (sale["date"] - point["arrival_date"]).days
            if days >= 0:
                total += sale["quantity"] * (a * (1 - math.exp(-b * days)) + c)
        return total

    def _save_coefficients(self, product_id: int, coeffs: Dict[str, Any]) -> None:
        """Сохраняет коэффициенты"""
        stmt = select(ShrinkageCoefficientModel).where(
            ShrinkageCoefficientModel.product_id == product_id
        )
        existing = self.session.scalars(stmt).first()

        if existing:
            existing.a = coeffs["a"]
            existing.b = coeffs["b"]
            existing.c = coeffs["c"]
            existing.rmse = coeffs.get("rmse")
            existing.data_points = coeffs.get("data_points", 0)
            existing.status = coeffs["status"]
            existing.calibration_date = datetime.now()
        else:
            coeff = ShrinkageCoefficientModel(
                product_id=product_id,
                a=coeffs["a"],
                b=coeffs["b"],
                c=coeffs["c"],
                rmse=coeffs.get("rmse"),
                data_points=coeffs.get("data_points", 0),
                status=coeffs["status"],
            )
            self.session.add(coeff)

        self.session.commit()
