from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean

from app.db.session import Base


class Supplier(Base):
    __tablename__ = 'supplier'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(id={self.id!r}, email={self.email!r})'
