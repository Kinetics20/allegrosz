from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

from app.db.base import Base


class Contact(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False)
    phone: Mapped[str] = mapped_column(String(14), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(id={self.id!r}, email={self.email!r})'
