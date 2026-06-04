from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repository.products import product_repository
from app.schemas.products import ProductRead, ProductCreate

router = APIRouter(prefix='/products', tags=['Products'])

DbSession = Annotated[AsyncSession, Depends(get_db)]
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
        product_id: int
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
