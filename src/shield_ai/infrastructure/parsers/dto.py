from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RowType(Enum):
    """
    Перечисление для типов строк в иерархическом Excel-отчёте.
    """
    HEADER = auto()
    GROUP_HEADER = auto()
    DATA = auto()
    TOTAL = auto()
    EMPTY = auto()
    UNDEFINED = auto()


class FlatRecord(BaseModel):
    """
    Pydantic-модель для хранения плоской записи данных из Excel-отчёта.
    
    Содержит все поля, указанные в спецификации data-model.md,
    с правильными типами данных для корректной валидации и обработки.
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
    metadata: Optional[Dict[str, Any]] = Field(None, description="Служебные метаданные для будущего расширения.")


class ParsingContext(BaseModel):
    """
    Pydantic-модель для хранения контекста парсинга.

    Используется для отслеживания текущего состояния (например, текущий склад,
    группа товаров) при итеративном обходе иерархической структуры
    Excel-файла.
    """
    warehouse: Optional[str] = None
    group: Optional[str] = None
    product: Optional[str] = None
    batch_code: Optional[str] = None
    batch_date: Optional[datetime] = None
    doc_type: Optional[str] = None
    doc_date: Optional[datetime] = None