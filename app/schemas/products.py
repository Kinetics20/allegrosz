from decimal import Decimal
import re

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None)
    price: Decimal = Field(..., gt=0, max_digits=9)
    sku: str = Field(..., min_length=5, max_length=9)

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, value):
        if not re.match(r'^[A-Z]+-\d+$', value):
            raise ValueError('SKU must be in the format CATEGORY-NUMBER (e.g., TECH-001).')
        return value.upper()


class ProductRead(ProductCreate):
    sku: str
    model_config = {'from_attributes': True}
