from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repository.products import product_repository
from app.schemas.products import ProductRead, ProductCreate, ProductUpdate
from app.services.products import get_product_or_404, ensure_sku_available

router = APIRouter(prefix='/products', tags=['Products'])

DbSession = Annotated[AsyncSession, Depends(get_db)]
ProductId = Annotated[
    int,
    Path(
        gt=0,
        description="Positive product identifier.",
        examples=[1],
    ),
]

PRODUCT_EXAMPLE = {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with USB receiver.",
    "sku": "TECH-001",
    "price": "129.99",
}


@router.get(
    "/",
    response_model=list[ProductRead],
    summary="List products",
    description=(
            "Returns products from the catalog with optional text search, price filtering, "
            "and pagination. The `search` parameter matches product name, description, "
            "and SKU. Use `skip` and `limit` for page-based browsing."
    ),
    response_description="A paginated list of products matching the provided filters.",
    responses={
        status.HTTP_200_OK: {
            "description": "Products returned successfully.",
            "content": {
                "application/json": {
                    "example": [PRODUCT_EXAMPLE]
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid filter range.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "min_price cannot be greater than max_price."
                    }
                }
            },
        },
    },
)
async def list_products(
        db: DbSession,
        search: Annotated[
            str | None,
            Query(
                min_length=1,
                max_length=100,
                description="Optional phrase matched against product name, description, and SKU.",
                examples=["mouse", "TECH-001"],
            ),
        ] = None,
        min_price: Annotated[
            Decimal | None,
            Query(
                gt=0,
                description="Minimum product price. Must be greater than zero.",
                examples=["10.00"],
            ),
        ] = None,
        max_price: Annotated[
            Decimal | None,
            Query(
                gt=0,
                description="Maximum product price. Must be greater than zero.",
                examples=["500.00"],
            ),
        ] = None,
        skip: Annotated[
            int,
            Query(
                ge=0,
                description="Number of products to skip before returning results.",
                examples=[0],
            ),
        ] = 0,
        limit: Annotated[
            int,
            Query(
                ge=1,
                le=100,
                description="Maximum number of products to return. Capped at 100.",
                examples=[20],
            ),
        ] = 100,
) -> list[ProductRead]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price.",
        )

    search_term = search.strip() if search else None
    return await product_repository.get_many(
        db,
        search=search_term,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit,
    )


@router.get('/{product_id}', response_model=ProductRead)
async def get_product(
        db: DbSession,
        product_id: ProductId
) -> ProductRead:
    product = await product_repository.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')

    return product


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


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Deletes a product from the catalog by its unique identifier.",
    response_description="Product deleted successfully.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Product deleted successfully.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Product was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": 'Product not found.'}
                }
            },
        }
    },
)
async def delete_product(
        db: DbSession,
        product_id: ProductId
) -> None:
    deleted = await product_repository.delete(db=db, product_id=product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Replace product",
    description=(
            "Replaces all editable product fields. Use this endpoint when the client "
            "sends a complete product payload."
    ),
    response_description="Product replaced successfully.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product replaced successfully.",
            "content": {
                "application/json": {
                    "example": {
                        **PRODUCT_EXAMPLE,
                        "name": "Wireless Mouse Pro",
                        "sku": "TECH-002",
                        "price": "149.99",
                    },
                }
            },
        },
    },
)
async def replace_product(
        db: DbSession,
        product_id: ProductId,
        product: ProductCreate
) -> ProductRead:
    await get_product_or_404(db, product_id)
    await ensure_sku_available(db, product_id, product.sku)

    try:
        updated_product = await product_repository.update(db, product_id, **product.model_dump())
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Product with this SKU already exists.')

    if updated_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')

    return updated_product


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update product",
    description=(
            "Partially updates a product. Send only fields that should change. "
            "`description` may be set to `null` to clear it."
    ),
    response_description="Product updated successfully.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product updated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        **PRODUCT_EXAMPLE,
                        "name": "Wireless Mouse Pro",
                        "price": "149.99",
                    },
                }
            },
        },
    },
)
async def update_product(
        db: DbSession,
        product_id: ProductId,
        product: ProductUpdate
) -> ProductRead:
    updates = product.model_dump(exclude_unset=True)

    if not updates:
        return await get_product_or_404(db, product_id)

    if 'sku' in updates:
        await ensure_sku_available(db, updates['sku'], product_id)

    try:
        updated_product = await product_repository.update(db, product_id, **updates)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Product with this SKU already exists.')

    if updated_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found.')

    return updated_product
