import re

from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")
MOBILE_REGEX = re.compile(r"^\+?\d{7,15}$")


class UserInfo(BaseModel):
    name: str = Field(min_length=1)
    email: str
    mobile: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty.")
        return v

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not EMAIL_REGEX.match(v):
            raise ValueError(f"'{v}' is not a valid email address.")
        return v

    @field_validator("mobile")
    @classmethod
    def mobile_must_be_valid(cls, v: str) -> str:
        v = v.strip().replace(" ", "").replace("-", "")
        if not MOBILE_REGEX.match(v):
            raise ValueError(f"'{v}' is not a valid mobile number (expected 7-15 digits).")
        return v


class CartItem(BaseModel):
    category: str = Field(min_length=1)
    item: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

    @field_validator("category", "item")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty.")
        return v


class ShippingAddress(BaseModel):
    address: str = Field(min_length=10)

    @field_validator("address")
    @classmethod
    def address_looks_real(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Address seems too short — please provide the full address.")
        return v