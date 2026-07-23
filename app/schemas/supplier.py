from pydantic import BaseModel, Field, EmailStr


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(..., max_length=50)
    phone: str | None = Field(None, min_length=7, max_length=30)
    active: bool = Field(True)


class SupplierRead(SupplierCreate):
    id: int
    model_config = {'from_attributes': True}


class SupplierUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=50
    )
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=30
    )
    active: bool | None = Field(
        default=None
    )
