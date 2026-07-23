from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier

class SupplierRepository:

    @staticmethod
    async def get(db: AsyncSession, supplier_id: int) -> Supplier | None:
        return await db.get(Supplier, supplier_id)

    @staticmethod
    async def create(db: AsyncSession, name: str, phone: str, email: str, active: bool) -> Supplier:
        supplier = Supplier(name=name, phone=phone, email=email, active=active)
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)
        return supplier

supplier_repository = SupplierRepository()