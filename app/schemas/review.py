from pydantic import BaseModel, PositiveInt, Field, field_validator, ConfigDict
from datetime import datetime


def normalize_required_text(value: str) -> str:
    value = ' '.join(value.split())

    if not value:
        raise ValueError('Author name cannot be blank.')

    return value


class ReviewCreate(BaseModel):
    product_id: PositiveInt = Field(..., gt=0)
    author_name: str = Field(..., min_length=5, max_length=100)
    rating: int = Field(..., ge=0, le=5)
    title: str = Field(..., min_length=5, max_length=150)
    comment: str = Field(..., max_length=2000)

    @field_validator('author_name', 'title')
    @classmethod
    def normalize_author_name(cls, value: str) -> str:
        return normalize_required_text(value)

    @field_validator('comment')
    @classmethod
    def normalize_comment(cls, value: str) -> str:
        return normalize_required_text(value)


class ReviewRead(ReviewCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=0, le=5)
    title: str = Field(..., min_length=5, max_length=150)
    comment: str = Field(..., max_length=1000)

    @field_validator('rating')
    @classmethod
    def normalize_rating(cls, value: str) -> str:
        return normalize_required_text(value)

    @field_validator('comment')
    @classmethod
    def normalize_comment(cls, value: str) -> str:
        return normalize_required_text(value)


class ReviewStats(BaseModel):
    product_id: int
    reviews_count: int
    average_rating: float | None
