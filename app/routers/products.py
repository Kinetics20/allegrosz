from typing import Annotated
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repository.products import product_repository
from app.schemas.products import ProductRead, ProductCreate

router = APIRouter(prefix='/products', tags=['Products'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get('/', response_model=list[ProductRead])
async def list_products(
        db: DbSession,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
) -> list[ProductRead]:
    if search:
        return await product_repository.search(db, search, skip=skip, limit=limit)

    return await product_repository.get_all(db, skip=skip, limit=limit)


@router.post('/', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: DbSession
) -> ProductCreate:
    return await product_repository.create(
        db=db,
        name=product.name,
        description=product.description,
        price=product.price,
        sku=product.sku
    )
