from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Dict,
    List,
)

from shield_ai.domain.entities.product import (
    Product,
)
from shield_ai.domain.entities.shrinkage_profile import (
    ShrinkageCoefficient,
)


class ProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Product]: ...


class CalibrationDataRepository(ABC):
    @abstractmethod
    def get_for_product(self, product_id: int) -> List[Dict[str, Any]]: ...


class CoefficientRepository(ABC):
    @abstractmethod
    def save(self, coeffs: ShrinkageCoefficient) -> None: ...
