from datetime import datetime, UTC

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, DateTime, text, FetchedValue

from app.db.session import Base

from app.models.location import Location
from app.models.products import Product


class InventoryItem(Base):
    __tablename__ = 'inventory_item'

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey('location.id'), primary_key=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reordered_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("now()"),
        server_onupdate=FetchedValue(),
    )

    product: Mapped['Product'] = relationship('Product', back_populates='inventory_items')
    location: Mapped['Location'] = relationship('Location', back_populates='inventory_items')

    def __repr__(self) -> str:
        return f'{type(self).__name__}(product_id={self.product_id!r}, loccation_id={self.location_id!r}, quantity={self.quantity!r})'
