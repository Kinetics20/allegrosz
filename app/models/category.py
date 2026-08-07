from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

from app.db.session import Base


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(id={self.id!r}, name={self.name!r})'
