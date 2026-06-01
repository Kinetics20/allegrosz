from decimal import Decimal

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
            select(Product).where(Product.sku == sku)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Product]:
        result = await db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

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

    @staticmethod
    async def filter_by_price(db: AsyncSession,
                              min_price: Decimal | None = None,
                              max_price: Decimal | None = None,
                              skip: int = 0, limit: int = 100
                              ) -> list[Product]:
        query = select(Product)

        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        result = await db.execute(
            query.offset(skip).limit(limit)
        )

        return list(result.scalars().all())

    @staticmethod
    async def create(
            db: AsyncSession,
            name: str,
            description: str | None,
            price: Decimal,
            sku: str
    ) -> Product:
        product = Product(name=name, description=description, price=price, sku=sku)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete(
            db: AsyncSession,
            product_id: int
    ) -> bool:
        product = await ProductRepository.get(db, product_id)
        if not product:
            return False

        await db.delete(product)
        await db.commit()
        return True

    @staticmethod
    async def update(
            db: AsyncSession,
            product_id: int,
            name: str | None,
            description: str | None,
            price: Decimal | None,
            sku: str | None
    ) -> Product | None:
        product = await ProductRepository.get(db, product_id)
        if not product:
            return None

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if sku is not None:
            product.sku = sku

        db.add(product)
        await db.commit()
        await db.refresh(product)

        return product


product_repository = ProductRepository()
