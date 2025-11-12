"""
Domain entities - Доменные сущности
"""
from .product import Product
from .batch import Batch
from .shrinkage_profile import ShrinkageProfile, CoefficientStatus

__all__ = ['Product', 'Batch', 'ShrinkageProfile', 'CoefficientStatus']
