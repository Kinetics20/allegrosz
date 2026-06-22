from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.location import LocationRead, LocationCreate, LocationUpdate, LocationWithStock
from app.db.session import get_db
from app.services.locations import get_location_or_404
from app.models.location import Location
from app.repository.location import location_repository

router = APIRouter(prefix='/locations', tags=['Locations'])


def build_location_with_stock(location: Location, total_stock: int) -> LocationWithStock:
    return LocationWithStock(
        id=location.id,
        name=location.name,
        address=location.address,
        capacity=location.capacity,
        total_stock=total_stock,
    )


DbSession = Annotated[AsyncSession, Depends(get_db)]
LocationId = Annotated[
    int,
    Path(
        gt=0,
        description='Positive location identifier.'
    ),
]


@router.get('/', response_model=list[LocationRead])
async def get_locations(db: DbSession, search: str | None = None, skip: int = 0, limit: int = 100) -> list[Location]:
    if search:
        return await location_repository.search(db, search.strip(), skip, limit)

    return await location_repository.get_all(db)


@router.get('/with-stock', response_model=list[LocationWithStock], status_code=status.HTTP_200_OK)
async def list_locations_with_stock(db: DbSession, skip: int = 0, limit: int = 100):
    locations = await location_repository.get_all_with_stock_counts(db, skip=skip, limit=limit)
    return [build_location_with_stock(location, total_stock) for location, total_stock in locations]


@router.get('/{location_id}', response_model=LocationRead)
async def get_location(db: DbSession, location_id: LocationId) -> Location:
    return await get_location_or_404(db, location_id)


@router.get('/{location_id}/stock', response_model=LocationWithStock, status_code=status.HTTP_200_OK)
async def location_with_stock(db: DbSession, location_id: LocationId) -> LocationWithStock:
    location_with_stock = await location_repository.get_with_stock_count(db, location_id)

    if not location_with_stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found.')

    location, stock = location_with_stock

    return build_location_with_stock(location, stock)


@router.post('/', response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(db: DbSession, location: LocationCreate) -> LocationRead:
    return await location_repository.create(
        db=db,
        name=location.name,
        address=location.address,
        capacity=location.capacity
    )


@router.put('/{location_id}', response_model=LocationRead, status_code=status.HTTP_200_OK)
async def replace_location(db: DbSession, location_id: LocationId, location: LocationCreate) -> LocationRead:
    await get_location_or_404(db, location_id)

    return await location_repository.update(db, location_id, **location.model_dump())


@router.patch('/{location_id}', response_model=LocationRead, status_code=status.HTTP_200_OK)
async def update_location(db: DbSession, location_id: LocationId, location: LocationUpdate) -> Location:
    updates = location.model_dump(exclude_unset=True)

    if not updates:
        return await get_location_or_404(db, location_id)

    return await location_repository.update(db, location_id, **updates)


@router.delete('/{location_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(db: DbSession, location_id: LocationId) -> None:
    deleted = await location_repository.delete(db=db, location_id=location_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found.')
