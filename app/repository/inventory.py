from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem


class InventoryRepository:
    UPDATE_FIELDS = frozenset({'quantity', 'reordered_point'})

    @staticmethod
    async def get(db: AsyncSession, product_id: int, location_id: int) -> InventoryItem | None:
        return await db.get(InventoryItem, (product_id, location_id))

    @staticmethod
    async def get_low_stock(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[InventoryItem]:
        result = await db.execute(
            select(InventoryItem).options(
                selectinload(
                    InventoryItem.product
                ),
                selectinload(
                    InventoryItem.location
                )
            ).where(
                InventoryItem.quantity < InventoryItem.reordered_point
            ).order_by(InventoryItem.product_id).offset(skip).limit(limit)
        )

        return list(result.scalars().all())




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
            ).order_by(InventoryItem.product_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_many(db: AsyncSession, product_id: int | None = None, location_id: int | None = None, skip: int = 0,
                       limit: int = 100) -> list[InventoryItem]:
        query = select(InventoryItem)

        if product_id is not None:
            query = query.where(InventoryItem.product_id == product_id)

        if location_id is not None:
            query = query.where(InventoryItem.location_id == location_id)

        result = await db.execute(
            query.order_by(InventoryItem.product_id, InventoryItem.location_id).offset(skip).limit(limit)
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
    async def get_by_location(db: AsyncSession, location_id: int, skip: int = 0, limit: int = 100) -> list[
        InventoryItem]:
        result = await db.execute(
            select(InventoryItem)
            .options(
                selectinload(
                    InventoryItem.product
                )
            )
            .where(InventoryItem.location_id == location_id).order_by(InventoryItem.product_id).offset(skip).limit(
                limit)
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_total_quantity_by_product(db: AsyncSession, product_id: int) -> int:
        result = await db.scalar(
            select(func.coalesce(func.sum(InventoryItem.quantity), 0))
            .where(InventoryItem.product_id == product_id)
        )
        return int(result or 0)

    @staticmethod
    async def create(db: AsyncSession, product_id: int, location_id: int, quantity: int,
                     reordered_point: int = 0) -> InventoryItem:
        inventory = InventoryItem(product_id=product_id, location_id=location_id, quantity=quantity,
                                  reordered_point=reordered_point
                                  )
        db.add(inventory)
        await db.commit()
        await db.refresh(inventory)
        return inventory

    @staticmethod
    async def delete(db: AsyncSession, product_id: int, location_id: int) -> bool:
        inventory = await InventoryRepository.get(db, product_id, location_id)
        if not inventory:
            return False

        await db.delete(inventory)
        await db.commit()
        return True

    @staticmethod
    async def set_stock(db: AsyncSession, product_id: int, location_id: int, quantity: int,
                        reordered_point: int | None = None) -> InventoryItem | None:
        if quantity < 0:
            return None

        inventory_item = await InventoryRepository.get(db, product_id, location_id)

        if not inventory_item:
            inventory_item = InventoryItem(product_id=product_id, location_id=location_id, quantity=quantity,
                                           reordered_point=reordered_point or 0)
        else:
            inventory_item.quantity = quantity
            if reordered_point is not None:
                inventory_item.reordered_point = reordered_point

        db.add(inventory_item)
        await db.commit()
        await db.refresh(inventory_item)
        return inventory_item

    @staticmethod
    async def update(db: AsyncSession, product_id: int, location_id: int, **fields: object) -> InventoryItem | None:
        inventory_item = await InventoryRepository.get(db, product_id, location_id)

        if not inventory_item:
            return None

        invalid_fields = set(fields) - InventoryRepository.UPDATE_FIELDS

        if invalid_fields:
            raise ValueError(f'Invalid inventory update fields: {', '.join(sorted(invalid_fields))}')

        if not fields:
            return inventory_item

        for field, value in fields.items():
            setattr(inventory_item, field, value)

        db.add(inventory_item)
        await db.commit()
        await db.refresh(inventory_item)

        return inventory_item
        

inventory_repository = InventoryRepository()
