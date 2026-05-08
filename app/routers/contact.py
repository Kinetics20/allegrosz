from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.contact import contact_repository
from app.schemas.contact import ContactRead, ContactCreate

from app.db.session import get_db

router = APIRouter(prefix='/contacts', tags=['Contacts'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[ContactRead])
async def list_contacts(
        db: DbSession,
        skip: int = 0,
        limit: int = 100,
) -> list[ContactRead]:
    return await contact_repository.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
        contact: ContactCreate,
        db: DbSession
) -> ContactRead:
    return await contact_repository.create(
        db=db,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        message=contact.message
    )


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
        contact_id: int,
        db: DbSession
) -> ContactRead:
    contact = await contact_repository.get(db=db, contact_id=contact_id)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: DbSession) -> None:
    deleted = await contact_repository.delete(db=db, contact_id=contact_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found.')
