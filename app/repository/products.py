from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.products import Product


class ProductRepository:
    UPDATE_FIELDS = frozenset({"name", "description", "sku", "price"})

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
    async def get_many(
            db: AsyncSession,
            search: str | None = None,
            min_price: Decimal | None = None,
            max_price: Decimal | None = None,
            skip: int = 0,
            limit: int = 100
    ) -> list[Product]:

        query = select(Product)

        if search:
            term = f'%{search}%'
            query = query.where(
                or_(
                    Product.name.ilike(term),
                    Product.description.ilike(term),
                    Product.sku.ilike(term)
                )
            )

        if min_price is not None:
            query = query.where(Product.price >= min_price)

        if max_price is not None:
            query = query.where(Product.price <= max_price)

        result = await db.execute(
            query.offset(skip).limit(limit)
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
            **fields: object

    ) -> Product | None:
        product = await ProductRepository.get(db, product_id)
        if not product:
            return None

        invalid_fields = set(fields) - ProductRepository.UPDATE_FIELDS

        if invalid_fields:
            raise ValueError(f'Invalid product update fields: {", ".join(sorted(invalid_fields))}.')

        if not fields:
            return product

        for field, value in fields.items():
            setattr(product, field, value)

        db.add(product)
        await db.commit()
        await db.refresh(product)

        return product


product_repository = ProductRepository()
