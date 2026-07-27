from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.supplier import supplier_repository
from app.db.session import get_db
from app.schemas.supplier import SupplierRead, SupplierCreate

router = APIRouter(prefix='/suppliers', tags=['Supplier'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get('/{supplier_id}', response_model=SupplierRead)
async def get_supplier(db: DbSession, supplier_id: int) -> SupplierRead:
    supplier = await supplier_repository.get(db=db, supplier_id=supplier_id)

    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")

    return supplier


@router.get('/', response_model=list[SupplierRead])
async def list_suppliers(db: DbSession, skip: int = 0, limit: int = 100) -> list[SupplierRead]:
    return await supplier_repository.get_all(db=db, skip=skip, limit=limit)


@router.post('/', response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(db: DbSession, supplier: SupplierCreate) -> SupplierRead:
    return await supplier_repository.create(
        db=db,
        name=supplier.name,
        email=supplier.email,
        phone=supplier.phone,
        active=supplier.active
    )


@router.delete('/{supplier_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int, db: DbSession) -> None:
    deleted = await supplier_repository.delete(db=db, supplier_id=supplier_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Supplier not found.')
