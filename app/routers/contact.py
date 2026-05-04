from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.contact import contact_repository
from app.schemas.contact import ContactRead

from app.api.deps import get_db

router = APIRouter(prefix='/contacts', tags=['Contacts'])


@router.get('/', response_model=list[ContactRead])
async def list_contacts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await contact_repository.get_all(db, skip, limit)
