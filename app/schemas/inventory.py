import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from app.schemas.location import LocationRead
from app.schemas.products import ProductRead


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
    reordered_point: int = Field(
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
    last_updated: datetime.datetime | None = Field(
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


class InventoryDetailRead(InventoryRead):
    product: ProductRead
    location: LocationRead


class InventoryWithProduct(InventoryRead):
    product: ProductRead


class InventoryWithLocation(InventoryRead):
    location: LocationRead


class InventorySetStock(BaseModel):
    quantity: int = Field(
        ...,
        ge=0,
        description="Absolute stock quantity to store.",
        examples=[75],
    )
    reorder_point: int | None = Field(
        default=None,
        ge=0,
        description="Optional new reorder point. Omit to keep the current value.",
        examples=[15],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity": 75,
                "reorder_point": 15,
            }
        }
    )


class InventoryUpdate(BaseModel):
    quantity: int | None = Field(
        default=None,
        ge=0,
        description="New absolute stock quantity. Omit to keep the current value.",
        examples=[80],
    )
    reorder_point: int | None = Field(
        default=None,
        ge=0,
        description="New reorder point. Omit to keep the current value.",
        examples=[20],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity": 80,
            }
        }
    )

    @field_validator("quantity", "reorder_point")
    @classmethod
    def validate_not_null(cls, value: int | None) -> int:
        if value is None:
            raise ValueError("Field cannot be null.")
        return value


class InventoryAdjustment(BaseModel):
    quantity_change: int = Field(
        ...,
        description="Quantity delta to apply. Use a negative value to remove stock.",
        examples=[5],
    )
    reorder_point: int | None = Field(
        default=None,
        ge=0,
        description="Optional new reorder point applied together with the stock change.",
        examples=[10],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_change": 5,
                "reorder_point": 10,
            }
        }
    )


class ProductInventoryTotal(BaseModel):
    product_id: PositiveInt
    total_quantity: int = Field(..., ge=0)