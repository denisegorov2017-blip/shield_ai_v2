"""
ORM модели SQLAlchemy 2.0 с современной типизацией (Mapped)
Синхронная работа
"""
from sqlalchemy import String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from .base import Base


class ProductModel(Base):
    """Товар"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    group_name: Mapped[str] = mapped_column(String(200), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Связи
    batches: Mapped[List["BatchModel"]] = relationship(
        "BatchModel", back_populates="product", cascade="all, delete-orphan"
    )
    inventories: Mapped[List["InventoryModel"]] = relationship(
        "InventoryModel", back_populates="product", cascade="all, delete-orphan"
    )
    coefficients: Mapped[Optional["ShrinkageCoefficientModel"]] = relationship(
        "ShrinkageCoefficientModel", back_populates="product", uselist=False, cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, name='{self.name}')>"


class BatchModel(Base):
    """Партия товара"""
    __tablename__ = "batches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    arrival_date: Mapped[str] = mapped_column(String(20), nullable=False)
    arrival_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    initial_qty: Mapped[float] = mapped_column(Float, nullable=False)
    remaining_qty: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Связи
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="batches")
    sales: Mapped[List["SaleModel"]] = relationship(
        "SaleModel", back_populates="batch", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<BatchModel(id={self.id}, product_id={self.product_id}, arrival='{self.arrival_date}')>"


class SaleModel(Base):
    """Продажа/расход"""
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey('batches.id'), nullable=False, index=True)
    sale_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    document_name: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Связи
    batch: Mapped["BatchModel"] = relationship("BatchModel", back_populates="sales")
    
    def __repr__(self) -> str:
        return f"<SaleModel(id={self.id}, batch_id={self.batch_id}, qty={self.quantity})>"


class InventoryModel(Base):
    """Инвентаризация"""
    __tablename__ = "inventories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    inventory_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    expected_qty: Mapped[float] = mapped_column(Float, nullable=False)
    actual_qty: Mapped[float] = mapped_column(Float, nullable=False)
    shrinkage: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Связи
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="inventories")
    
    def __repr__(self) -> str:
        return f"<InventoryModel(id={self.id}, product_id={self.product_id}, date='{self.inventory_date}')>"


class ShrinkageCoefficientModel(Base):
    """Коэффициенты усушки для товара"""
    __tablename__ = "shrinkage_coefficients"
    
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    a: Mapped[float] = mapped_column(Float, nullable=False)
    b: Mapped[float] = mapped_column(Float, nullable=False)
    c: Mapped[float] = mapped_column(Float, nullable=False)
    rmse: Mapped[Optional[float]] = mapped_column(Float)
    data_points: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(50), default="стандартные")
    calibration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Связи
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="coefficients")
    
    def __repr__(self) -> str:
        return f"<ShrinkageCoefficientModel(product_id={self.product_id}, a={self.a:.4f}, b={self.b:.4f}, c={self.c:.4f})>"
