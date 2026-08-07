from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import ProductReview


class ReviewRepository:

    @staticmethod
    async def get(db: AsyncSession, review_id: int) -> ProductReview:
        return await db.get(ProductReview, review_id)

    @staticmethod
    async def create(db: AsyncSession, **fields: object) -> ProductReview:
        review = ProductReview(**fields)

        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

review_repository = ReviewRepository()
