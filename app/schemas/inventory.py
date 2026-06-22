from datetime import datetime

from pydantic import PositiveInt, BaseModel, Field, ConfigDict


class InventoryCreate(BaseModel):
    product_id: PositiveInt = Field(
        ...,
        description="Product identifier.",
        examples=[1],
    )
    location_id: PositiveInt = Field(
        ...,
        description="Location identifier.",
        examples=[1],
    )
    quantity: int = Field(
        ...,
        ge=0,
        description="Current stock quantity at the location.",
        examples=[50],
    )
    reorder_point: int = Field(
        default=0,
        ge=0,
        description="Quantity threshold below which the item is considered low stock.",
        examples=[10],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "location_id": 1,
                "quantity": 50,
                "reorder_point": 10,
            }
        }
    )


class InventoryRead(InventoryCreate):
    last_updated: datetime | None = Field(
        default=None,
        description="Timestamp of the last stock update.",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "product_id": 1,
                "location_id": 1,
                "quantity": 50,
                "reorder_point": 10,
                "last_updated": "2026-06-12T12:00:00Z",
            }
        },
    )
