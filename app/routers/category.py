from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.repository.category import category_repository
from app.schemas.category import CategoryRead, CategoryCreate

router = APIRouter(prefix='/category', tags=['Category'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def ensure_name_available(db, name: str, category_id: int | None = None) -> None:
    category = await category_repository.get_by_name(db, name)

    if category is not None and category.id != category_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category with this name already exists.')


@router.get('/{category_id}', response_model=CategoryRead)
async def get_category(category_id: int, db: DbSession) -> CategoryRead:
    category = await category_repository.get(db, category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found.')

    return category


@router.get('/by_name/{name}', response_model=CategoryRead)
async def get_category_by_name(db: DbSession, name: str) -> CategoryRead:
    category = await category_repository.get_by_name(db, name)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category's name not found.")

    return category


@router.get('/', response_model=list[CategoryRead])
async def list_categories(db: DbSession, skip: int = 0, limit: int = 100) -> list[CategoryRead]:
    return await category_repository.get_all(db, skip=skip, limit=limit)


@router.post('/', response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: DbSession) -> CategoryRead:
    await ensure_name_available(db, category.name)

    try:
        return await category_repository.create(
            db=db, name=category.name, description=category.description
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category name already exists.')


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: DbSession) -> None:
    deleted = await category_repository.delete(db=db, category_id=category_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found.')
