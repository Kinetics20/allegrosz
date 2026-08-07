from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.category import Category

class CategoryRepository:

    @staticmethod
    async def get(db: AsyncSession, category_id: int) -> Category | None:
        return await db.get(Category, category_id)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Category | None:
        category = await db.execute(select(Category).where(Category.name==name))

        return category.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
        result = await db.execute(
            select(Category).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, name: str, description: str | None = None) -> Category:
        category = Category(name=name, description=description)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete(db: AsyncSession, category_id: int) -> bool:
        category = await CategoryRepository.get(db, category_id)
        if not category:
            return False

        await db.delete(category)
        await db.commit()
        return True

category_repository = CategoryRepository()