from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator


class LocationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
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


class LocationWithStock(LocationRead):
    total_stock: int = Field(
        ...,
        ge=0,
        description="Total quantity currently stored at this location.",
        examples=[137],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Main Warehouse",
                "address": "123 Storage Ave, Warehouse District",
                "capacity": 1000,
                "total_stock": 137,
            }
        },
    )


class LocationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New location display name. Omit to keep the current value.",
        examples=["Secondary Warehouse"],
    )
    address: str | None = Field(
        default=None,
        min_length=5,
        max_length=200,
        description="New location address. Omit to keep the current value.",
        examples=["456 Logistics Park"],
    )
    capacity: PositiveInt | None = Field(
        default=None,
        description="New maximum stock capacity. Omit to keep the current value.",
        examples=[750],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Secondary Warehouse",
                "capacity": 750,
            }
        }
    )

    @field_validator("name", "address", "capacity")
    @classmethod
    def validate_not_null(cls, value: object | None) -> object:
        if value is None:
            raise ValueError("Field cannot be null.")
        return value
