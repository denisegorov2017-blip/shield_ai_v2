"""
Domain entities - Доменные сущности
"""

from .batch import Batch
from .product import Product
from .shrinkage_profile import CoefficientStatus, ShrinkageProfile

__all__ = ["Product", "Batch", "ShrinkageProfile", "CoefficientStatus"]
