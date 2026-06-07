from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from app.models.products import Product

from app.repository.products import product_repository


async def get_product_or_404(db: AsyncSession, product_id: int) -> Product:
    product = await product_repository.get(db, product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')

    return product

async def ensure_sku_available(db: AsyncSession, product_id: int, sku: str) -> None:
    product = await product_repository.get_by_sku(db, sku)

    if product is not None and product.id != product_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Product with this SKU already exists.')
