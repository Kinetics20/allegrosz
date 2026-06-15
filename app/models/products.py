from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Numeric

from app.db.session import Base



class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=2), nullable=False)
    sku: Mapped[str] = mapped_column(String(9), nullable=False, unique=True, index=True)

    inventory_items: Mapped[list['InventoryItem']] = relationship('InventoryItem', back_populates='product', cascade='all, delete')

    def __repr__(self) -> str:
        return f'{type(self).__name__}(id={self.id!r}, name={self.name!r}, sku={self.sku!r})'
