"""
Этот модуль определяет контракт данных для плоской записи инвентаризации.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from pydantic import BaseModel, Field


class FlatRecord(BaseModel):
    """
    Представляет единую плоскую запись движения по складу, преобразованную
    из иерархического отчета Excel.
    """
    warehouse: str = Field(..., description="Склад, на котором произошла транзакция.")
    group: str = Field(..., description="Товарная группа.")
    product: str = Field(..., description="Наименование конкретного товара.")
    batch_code: str = Field(..., description="Уникальный идентификатор партии. Создается только приходным документом.")
    batch_date: datetime = Field(..., description="Дата прихода партии. Важно для FIFO и отслеживания срока годности.")
    doc_type: str = Field(..., description="Тип документа движения (например, 'Поступление', 'Реализация').")
    doc_date: datetime = Field(..., description="Дата документа движения. Должна быть с таймзоной для избежания несостыковок.")
    qty_begin: Decimal = Field(..., description="Начальное количество до транзакции.")
    qty_in: Decimal = Field(..., description="Количество поступления.")
    qty_out: Decimal = Field(..., description="Количество расхода.")
    qty_end: Decimal = Field(..., description="Конечное количество после транзакции.")
    unit: str = Field(..., description="Единица измерения (например, 'кг', 'шт').")
    comment: Optional[str] = Field(None, description="Необязательный комментарий к записи.")
    metadata: Optional[Dict] = Field(None, description="Служебные метаданные для будущего расширения.")

    class Config:
        """Конфигурация Pydantic модели."""
        json_encoders = {
            Decimal: lambda v: f"{v:.3f}"  # Форматировать Decimal до 3 знаков в JSON
        }
        orm_mode = True
        allow_population_by_field_name = True