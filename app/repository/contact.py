from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.contact import Contact


class ContactRepository:

    @staticmethod
    async def get(db: AsyncSession, contact_id: int) -> Contact | None:
        return await db.get(Contact, contact_id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Contact]:
        result = await db.execute(
            select(Contact).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, name: str, email: str, phone: str, message: str) -> Contact:
        contact = Contact(name=name, email=email, phone=phone, message=message)
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def delete(db: AsyncSession, contact_id: int) -> bool:
        contact = await ContactRepository.get(db, contact_id)
        if not contact:
            return False

        await db.delete(contact)
        await db.commit()
        return True


contact_repository = ContactRepository()
