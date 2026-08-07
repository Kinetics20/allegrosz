from pydantic import BaseModel, Field, field_validator, ConfigDict


def normalize_category_name(value: str) -> str:
    value = value.strip().casefold()

    if not value:
        raise ValueError('Category name cannot be blank.')

    return value


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    description: str | None = Field(None)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_category_name(value)


class CategoryRead(CategoryCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=150)
    description: str | None = Field(None)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('Category name cannot null.')

        return normalize_category_name(value)
