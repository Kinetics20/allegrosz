from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=25)
    email: EmailStr = Field(..., max_length=40)
    phone: str = Field(..., min_length=7, max_length=14)
    message: str = Field(..., min_length=1)


class ContactRead(ContactCreate):
    id: int
    model_config = {'from_attributes': True}
