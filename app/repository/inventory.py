from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem

class InventoryRepository:

    @staticmethod
    async def get(db: AsyncSession, product_id: int, location_id: int) -> InventoryItem | None:
        return await db.get(InventoryItem, (product_id, location_id))


    @staticmethod
    async def get_detail(db: AsyncSession, product_id: int, location_id: int) -> InventoryItem | None:
        result = await db.execute(
            select(InventoryItem).options(
                selectinload(
                    InventoryItem.product
                ),
                selectinload(
                    InventoryItem.location
                )
            ).where(
               InventoryItem.product_id == product_id,
                InventoryItem.location_id == location_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_many(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[InventoryItem]:
        result = await db.execute(
            select(InventoryItem).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_product(db: AsyncSession, product_id: int, skip: int = 0, limit: int = 100) -> list[InventoryItem]:
        result = await db.execute(
            select(InventoryItem)
            .options(
                selectinload(
                    InventoryItem.location
                )
            )
            .where(InventoryItem.product_id == product_id).order_by(InventoryItem.location_id).offset(skip).limit(limit)
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_by_location(db: AsyncSession, location_id: int, skip: int = 0, limit: int = 100) -> list[InventoryItem]:
        result = await db.execute(
            select(InventoryItem)
            .options(
                selectinload(
                    InventoryItem.product
                )
            )
            .where(InventoryItem.location_id == location_id).order_by(InventoryItem.product_id).offset(skip).limit(limit)
        )

        return list(result.scalars().all())


