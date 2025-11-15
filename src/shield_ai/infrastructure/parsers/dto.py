from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Dict, Any
from pydantic import BaseModel


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
    warehouse: str
    group: str
    product: str
    batch_code: str
    batch_date: datetime
    doc_type: str
    doc_date: datetime
    qty_begin: Decimal
    qty_in: Decimal
    qty_out: Decimal
    qty_end: Decimal
    unit: str
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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