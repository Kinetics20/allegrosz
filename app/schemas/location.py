from pydantic import BaseModel, Field, PositiveInt, ConfigDict


class LocationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Location display name.",
        examples=["Main Warehouse"],
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Street address or operational location description.",
        examples=["123 Storage Ave, Warehouse District"],
    )
    capacity: PositiveInt = Field(
        ...,
        description="Maximum stock capacity for this location.",
        examples=[1000],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Main Warehouse",
                "address": "123 Storage Ave, Warehouse District",
                "capacity": 1000,
            }
        }
    )


class LocationRead(LocationCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Main Warehouse",
                "address": "123 Storage Ave, Warehouse District",
                "capacity": 1000,
            }
        },
    )