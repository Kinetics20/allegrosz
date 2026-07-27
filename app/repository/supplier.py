from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.supplier import Supplier

class SupplierRepository:

    @staticmethod
    async def get(db: AsyncSession, supplier_id: int) -> Supplier | None:
        return await db.get(Supplier, supplier_id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Supplier]:
        result = await db.execute(
            select(Supplier).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, name: str, phone: str, email: str, active: bool) -> Supplier:
        supplier = Supplier(name=name, phone=phone, email=email, active=active)
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)
        return supplier

    @staticmethod
    async def delete(db: AsyncSession, supplier_id: int) -> bool:
        supplier = await SupplierRepository.get(db, supplier_id)
        if not supplier:
            return False

        await db.delete(supplier)
        await db.commit()
        return True

supplier_repository = SupplierRepository()