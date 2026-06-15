from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from app.models import Location
from app.schemas.location import LocationRead, LocationCreate
from app.db.session import get_db
from app.services.locations import get_location_or_404
from app.models.location import Location
from app.repository.location import location_repository

router = APIRouter(prefix='/locations', tags=['Locations'])

DbSession = Annotated[AsyncSession, Depends(get_db)]
LocationId = Annotated[
    int,
    Path(
        gt=0,
        description='Positive location identifier.'
    ),
]


@router.get('/{location_id}', response_model=LocationRead)
async def get_location(db: DbSession, location_id: LocationId) -> Location:
    return await get_location_or_404(db, location_id)


@router.get('/', response_model=list[LocationRead])
async def get_locations(db: DbSession, search: str | None = None, skip: int = 0, limit: int = 100):
    if search:
        return await location_repository.search(db, search.strip(), skip, limit)

    return await location_repository.get_all(db)


@router.post('/', response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(db: DbSession, location: LocationCreate) -> LocationRead:
    return await location_repository.create(
        db=db,
        name=location.name,
        address=location.address,
        capacity=location.capacity
    )


@router.delete('/{location_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(db: DbSession, location_id: LocationId) -> None:
    deleted = await location_repository.delete(db=db, location_id=location_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found.')
