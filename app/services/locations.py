from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Location
from app.repository.location import location_repository


async def get_location_or_404(db: AsyncSession, location_id: int) -> Location:
    location = await location_repository.get(db, location_id)

    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found.')

    return location
