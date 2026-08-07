from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.review import ReviewRead, ReviewCreate
from app.repository.review import review_repository

router = APIRouter(prefix='/rewiews', tags=['Reviews'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get('/review_id', response_model=ReviewRead)
async def get_review(db: DbSession, review_id: int) -> ReviewRead:
    review = await review_repository.get(db, review_id)

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found.')
    return review


@router.post('/', response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, db: DbSession) -> ReviewRead:
    return await review_repository.create(
        db=db,
        product_id=review.product_id,
        author_name=review.author_name,
        rating=review.rating,
        title=review.title,
        comment=review.comment
    )
