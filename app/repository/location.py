from sqlalchemy import select, or_, func

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InventoryItem
from app.models.location import Location


class LocationRepository:

    @staticmethod
    async def get(db: AsyncSession, location_id: int) -> Location | None:
        return await db.get(Location, location_id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Location]:
        result = await  db.execute(
            select(Location).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def search(db: AsyncSession, term: str, skip: int = 0, limit: int = 100) -> list[Location]:
        result = await db.execute(
            select(Location).where(
                or_(
                    Location.name.ilike(f'%{term}%'),
                    Location.address.ilike(f'%{term}%')
                )
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_with_stock_count(db: AsyncSession, location_id: int) -> tuple[Location, int] | None:
        location = await LocationRepository.get(db, location_id)
        if not location:
            return None

        stock_count = await db.scalar(
            select(func.coalesce(func.sum(InventoryItem.quantity), 0)).where(InventoryItem.location_id == location_id)

        )

        return location, int(stock_count or 0)

    @staticmethod
    async def get_all_with_stock_counts(db: AsyncSession, skip: int = 0, limit: int = 0) -> list[tuple[Location, int]]:
        locations = await LocationRepository.get_all(db, skip, limit)
        if not locations:
            return []

        location_ids = [location.id for location in locations]

        stock_subquery = (
            select(
                InventoryItem.location_id,
                func.coalesce(func.sum(InventoryItem.quantity), 0).label('total_stock')

            )
            .where(InventoryItem.location_id.in_(location_ids))
            .group_by(InventoryItem.location_id)
            .subquery()
        )

        stock_counts: dict[int, int] = {}

        result = await db.execute(select(stock_subquery))

        for row in result.all():
            stock_counts[row.location_id] = int(row.total_stock or 0)

        result = []

        for location in locations:
            stock = stock_counts.get(location.id, 0)
            result.append((location, stock))

        return result

    @staticmethod
    async def create(db: AsyncSession, name: str, address: str, capacity: int) -> Location:
        location = Location(name=name, address=address, capacity=capacity)
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    @staticmethod
    async def delete(db: AsyncSession, location_id: int) -> bool:
        location = await LocationRepository.get(db, location_id)
        if not location:
            return False

        await db.delete(location)
        await db.commit()
        return True


location_repository = LocationRepository()
