from datetime import datetime
from decimal import Decimal

import phonenumbers
from phonenumbers import NumberParseException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field


def normalize_phone(value: str) -> str:
    try:
        # Si no viene con +código de país, asumimos Argentina.
        parsed = phonenumbers.parse(value, "AR")
    except NumberParseException:
        raise ValueError("Invalid phone number")

    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")

    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164
    )


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None):
        if value is None:
            return None

        return str(value).lower()


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    active: bool | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_phone(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None):
        if value is None:
            return None

        return str(value).lower()


class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int

class ProfessionalCreate(BaseModel):
    first_name: str
    last_name: str
    specialty: str | None = None
    license_number: str | None = None
    phone: str | None = None
    email: EmailStr | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("specialty", "license_number")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_phone(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None):
        if value is None:
            return None

        return str(value).lower()

class ProfessionalUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    license_number: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    active: bool | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("specialty", "license_number")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_phone(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None):
        if value is None:
            return None

        return str(value).lower()

class ProfessionalResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str | None
    license_number: str | None
    phone: str | None
    email: EmailStr | None
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class ProfessionalListResponse(BaseModel):
    items: list[ProfessionalResponse]
    total: int
    page: int
    page_size: int

class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    estimated_duration_minutes: int = Field(gt=0)
    initial_price: Decimal = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Service name cannot be blank")

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    estimated_duration_minutes: int | None = Field(
        default=None,
        gt=0
    )
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Service name cannot be blank")

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

class ServicePriceCreate(BaseModel):
    amount: Decimal = Field(ge=0)


class ServicePriceResponse(BaseModel):
    id: int
    service_id: int
    amount: Decimal
    valid_from: datetime
    valid_until: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    estimated_duration_minutes: int
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    prices: list[ServicePriceResponse]

    model_config = ConfigDict(
        from_attributes=True
    )

class ServiceListResponse(BaseModel):
    items: list[ServiceResponse]
    total: int
    page: int
    page_size: int