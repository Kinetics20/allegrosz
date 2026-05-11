from unittest import result

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.products import Product


class ProductRepository:

    @staticmethod
    async def get(db: AsyncSession, product_id: int) -> Product | None:
        return await db.get(Product, product_id)

    @staticmethod
    async def get_by_sku(db: AsyncSession, sku: str) -> Product | None:
        result = await db.execute(
            select(Product).where(Product.sku==sku)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Product]:
        result = await db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return  list(result.scalars().all())

    @staticmethod
    async def search(db: AsyncSession, term: str, skip: int = 0, limit: int = 100) -> list[Product]:
        result = await db.execute(
            select(Product).where(
                or_(
                    Product.name.ilike(f'%{term}%'),
                    Product.description.ilike(f'%{term}%'),
                    Product.sku.ilike(f'%{term}%')
                )

            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
