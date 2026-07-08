from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InventoryItem
from app.db.session import get_db
from app.repository.inventory import inventory_repository
from app.repository.products import product_repository
from app.repository.location import location_repository
from app.schemas.inventory import InventoryRead, InventoryCreate, InventoryWithLocation

router = APIRouter(prefix='/inventory', tags=['Inventory'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def ensure_product_exists(db: AsyncSession, product_id: int) -> None:
    product = await product_repository.get(db, product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')


async def ensure_location_exists(db: AsyncSession, location_id: int) -> None:
    location = await location_repository.get(db, location_id)

    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found.')


@router.get('/', response_model=list[InventoryRead])
async def get_inventory(db: DbSession, product_id: Annotated[int | None, Query(gt=0)] = None,
                        location_id: Annotated[int | None, Query(gt=0)] = None, skip: int = 0, limit: int = 100) -> \
        list[
            InventoryItem]:
    return await inventory_repository.get_many(db, product_id, location_id, skip, limit)


@router.post('/', response_model=InventoryRead)
async def create_inventory(db: DbSession, inventory: InventoryCreate) -> InventoryItem:
    await ensure_product_exists(db, inventory.product_id)
    await ensure_location_exists(db, inventory.location_id)

    existing_item = await inventory_repository.get(db, inventory.product_id, inventory.location_id)

    if existing_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Inventory already exists .')

    try:
        return await inventory_repository.create(
            db=db,
            product_id=inventory.product_id,
            location_id=inventory.location_id,
            quantity=inventory.quantity,
            reordered_point=inventory.reordered_point
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Inventory already exists.')


@router.get('/products/{product_id}', response_model=list[InventoryWithLocation])
async def list_inventory_by_product(db: DbSession, product_id: int, skip: int = 0, limit: int = 100) -> list[
    InventoryItem]:
    await ensure_product_exists(db, product_id)

    return await inventory_repository.get_by_product(db, product_id, skip, limit)
