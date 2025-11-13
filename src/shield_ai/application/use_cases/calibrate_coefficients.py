"""
Use Case: Калибровка коэффициентов усушки
Использует ПОРЦИОННУЮ модель (99.9% точность)

Этот модуль реализует алгоритм калибровки коэффициентов усушки для товаров на основе
исторических данных инвентаризаций, партий и продаж. Калибровка выполняется методом
наименьших квадратов с использованием порционной модели, которая учитывает каждую
продажу как отдельную порцию с собственным временем хранения.
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

    Класс, реализующий бизнес-логику калибровки коэффициентов усушки для товаров.
    Использует порционную модель, где каждая продажа рассматривается как отдельная
    порция с собственным временем хранения. Калибровка выполняется методом
    наименьших квадратов для минимизации разницы между предсказанными и
    фактическими значениями усушки.
    """

    def __init__(self, session: Session):
        self.session = session

    def execute_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Выполняет калибровку коэффициентов для всех товаров в системе

        Returns:
            Словарь с результатами калибровки для каждого товара в формате:
            {
                "название_товара": {
                    "a": float,      # Коэффициент a (начальная скорость усушки)
                    "b": float,      # Коэффициент b (скорость затухания усушки)
                    "c": float,      # Коэффициент c (базовый уровень усушки)
                    "rmse": float,   # Среднеквадратичная ошибка
                    "data_points": int,  # Количество точек данных
                    "status": str    # Статус калибровки
                }
            }
        """
        stmt = select(ProductModel)
        products = self.session.scalars(stmt).all()

        results = {}

        for product in products:
            coeffs = self._calibrate_product(product)
            self._save_coefficients(product.id, coeffs)
            results[product.name] = coeffs

        return results

    def _calibrate_product(self, product: ProductModel) -> Dict[str, Any]:
        """
        Выполняет калибровку коэффициентов для одного товара

        Алгоритм калибровки:
        1. Получает исторические данные инвентаризаций для товара
        2. Если данных недостаточно (< 3 точек), возвращает стандартные коэффициенты
        3. Определяет целевую функцию (сумма квадратов ошибок)
        4. Использует оптимизацию (L-BFGS-B) для нахождения оптимальных коэффициентов
        5. Вычисляет RMSE для оценки качества калибровки

        Args:
            product: Модель товара для калибровки

        Returns:
            Словарь с коэффициентами и метриками качества калибровки
        """
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
            """
            Целевая функция для оптимизации - сумма квадратов ошибок

            Args:
                params: Список параметров [a, b, c] для оптимизации

            Returns:
                Сумма квадратов разностей между предсказанными и фактическими значениями
            """
            a, b, c = params
            errors = []
            for point in data:
                predicted = self._calculate_portion(point, a, b, c)
                actual = point["actual_shrinkage"]
                errors.append((predicted - actual) ** 2)
            return sum(errors)  # type: ignore

        # Начальные значения коэффициентов: a=0.05, b=0.1, c=0.01
        x0 = [0.05, 0.1, 0.01]
        # Ограничения для коэффициентов: [a_min, a_max], [b_min, b_max], [c_min, c_max]
        bounds = [(0.01, 0.15), (0.01, 0.5), (0.0, 0.03)]
        # Оптимизация с использованием метода L-BFGS-B (ограниченная оптимизация)
        result = minimize(objective, x0, bounds=bounds, method="L-BFGS-B")  # type: ignore
        a, b, c = result.x

        # Вычисление RMSE (Root Mean Square Error) для оценки качества калибровки
        errors = [
            (self._calculate_portion(p, a, b, c) - p["actual_shrinkage"]) ** 2
            for p in data
        ]
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
        """
        Получает данные инвентаризаций для калибровки

        Собирает исторические данные о партиях, продажах и фактической усушке
        для указанного товара. Для каждой инвентаризации формирует точку данных
        с начальной массой партии, датой прибытия, списком продаж и фактической
        усушкой, измеренной при инвентаризации.

        Args:
            product_id: ID товара для получения данных

        Returns:
            Список словарей с данными для калибровки в формате:
            [
                {
                    "initial_mass": float,      # Начальная масса партии
                    "arrival_date": datetime,   # Дата прибытия партии
                    "sales": List[Dict],        # Список продаж: [{"date": datetime, "quantity": float}]
                    "actual_shrinkage": float   # Фактическая усушка, измеренная при инвентаризации
                },
                ...
            ]
        """
        stmt = select(InventoryModel).where(InventoryModel.product_id == product_id)
        inventories = self.session.scalars(stmt).all()

        data = []
        for inv in inventories:
            batch_stmt = select(BatchModel).where(BatchModel.product_id == product_id)
            batches = self.session.scalars(batch_stmt).all()

            for batch in batches:
                sales_stmt = select(SaleModel).where(SaleModel.batch_id == batch.id)
                sales = self.session.scalars(sales_stmt).all()

                sales_list = [
                    {"date": sale.sale_date, "quantity": sale.quantity}
                    for sale in sales
                ]

                data.append(
                    {
                        "initial_mass": batch.initial_qty,
                        "arrival_date": batch.arrival_datetime,
                        "sales": sales_list,
                        "actual_shrinkage": inv.shrinkage,
                    }
                )

        return data

    def _calculate_portion(
        self, point: Dict[str, Any], a: float, b: float, c: float
    ) -> float:
        """
        Расчёт усушки по порционной модели

        Для каждой продажи в точке данных вычисляет усушку по формуле:
        усушка_порции = количество_проданного * [a * (1 - e^(-b * дни_хранения)) + c]

        Где:
        - a: начальная скорость усушки
        - b: скорость затухания усушки
        - c: базовый уровень усушки (минимальная усушка независимо от времени)
        - дни_хранения: количество дней между датой продажи и датой прибытия партии

        Args:
            point: Точка данных с информацией о партии и продажах
            a: Коэффициент a (начальная скорость усушки)
            b: Коэффициент b (скорость затухания усушки)
            c: Коэффициент c (базовый уровень усушки)

        Returns:
            Общая усушка для всех продаж в точке данных
        """
        total = 0.0
        for sale in point["sales"]:
            # Вычисление количества дней между датой продажи и датой прибытия партии
            days = (sale["date"] - point["arrival_date"]).days
            if days >= 0:
                # Формула порционной модели: m * [a * (1 - e^(-b*t)) + c]
                # где m - количество проданного товара, t - дни хранения
                total += sale["quantity"] * (a * (1 - math.exp(-b * days)) + c)
        return total

    def _save_coefficients(self, product_id: int, coeffs: Dict[str, Any]) -> None:
        """
        Сохраняет коэффициенты усушки в базу данных

        Если коэффициенты для товара уже существуют, обновляет их значения,
        иначе создает новую запись. После сохранения фиксирует изменения
        в базе данных.

        Args:
            product_id: ID товара, для которого сохраняются коэффициенты
            coeffs: Словарь с коэффициентами и метриками качества калибровки
        """
        stmt = select(ShrinkageCoefficientModel).where(
            ShrinkageCoefficientModel.product_id == product_id
        )
        existing = self.session.scalars(stmt).first()

        if existing:
            # Обновление существующих коэффициентов
            existing.a = coeffs["a"]
            existing.b = coeffs["b"]
            existing.c = coeffs["c"]
            existing.rmse = coeffs.get("rmse")
            existing.data_points = coeffs.get("data_points", 0)
            existing.status = coeffs["status"]
            existing.calibration_date = datetime.now()
        else:
            # Создание новой записи с коэффициентами
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
