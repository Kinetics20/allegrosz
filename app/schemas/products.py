from decimal import Decimal, ROUND_HALF_UP
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


SKU_PATTERN = re.compile(r"^[A-Z]+-\d+$")
MAX_PRODUCT_PRICE = Decimal("10000")
PRICE_QUANT = Decimal("0.01")


def normalize_sku(value: str) -> str:
    value = value.upper()
    if not SKU_PATTERN.fullmatch(value):
        raise ValueError("SKU must be in the format CATEGORY-NUMBER (e.g., TECH-001).")
    return value


def normalize_price(value: Decimal) -> Decimal:
    value = value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)
    if value > MAX_PRODUCT_PRICE:
        raise ValueError("Price cannot exceed $10,000.")
    return value


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product display name.",
        examples=["Wireless Mouse"],
    )
    description: str | None = Field(
        default=None,
        description="Optional product description shown in the catalog.",
        examples=["Ergonomic wireless mouse with USB receiver."],
    )
    sku: str = Field(
        ...,
        min_length=5,
        max_length=9,
        description="Unique stock keeping unit in CATEGORY-NUMBER format.",
        examples=["TECH-001"],
    )
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        description="Product price. Must be greater than zero and cannot exceed 10000.",
        examples=["129.99"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with USB receiver.",
                "sku": "TECH-001",
                "price": "129.99",
            }
        }
    )

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        return normalize_sku(value)

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        return normalize_price(value)


class ProductRead(ProductCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with USB receiver.",
                "sku": "TECH-001",
                "price": "129.99",
            }
        },
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New product display name. Omit the field to keep the current value.",
        examples=["Wireless Mouse Pro"],
    )
    description: str | None = Field(
        default=None,
        description="New product description. Send null to clear the description.",
        examples=["Updated ergonomic mouse with silent buttons."],
    )
    sku: str | None = Field(
        default=None,
        min_length=5,
        max_length=9,
        description="New unique SKU in CATEGORY-NUMBER format.",
        examples=["TECH-002"],
    )
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        description="New product price. Omit the field to keep the current value.",
        examples=["149.99"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Wireless Mouse Pro",
                "price": "149.99",
            }
        }
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Name cannot be null.")
        return value

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("SKU cannot be null.")
        return normalize_sku(value)

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal | None) -> Decimal:
        if value is None:
            raise ValueError("Price cannot be null.")
        return normalize_price(value)