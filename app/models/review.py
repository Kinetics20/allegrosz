from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Text, DateTime, func, FetchedValue, CheckConstraint
from datetime import datetime

from app.db.session import Base
from app.models.products import Product


class ProductReview(Base):
    __tablename__ = 'product_review'
    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='ck_product_review_rating'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),
                                                 server_onupdate=FetchedValue())
    product: Mapped['Product'] = relationship('Product', back_populates='reviews')
