from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from app.db.session import Base

if TYPE_CHECKING:
    from app.models import InventoryItem


class Location(Base):
    __tablename__ = 'location'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    inventory_items: Mapped[list['InventoryItem']] = relationship('InventoryItem', back_populates='location',
                                                                  cascade='all, delete')

    def __repr__(self) -> str:
        return f'{type(self).__name__}(id={self.id!r}, name={self.name!r})'
