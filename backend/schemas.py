from datetime import datetime
from decimal import Decimal
from typing import Literal
import phonenumbers
from phonenumbers import NumberParseException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field, model_validator


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

AppointmentStatus = Literal[
    "scheduled",
    "confirmed",
    "completed",
    "cancelled",
    "no_show",
]

class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)
    professional_id: int = Field(gt=0)
    service_id: int | None = Field(default=None, gt=0)

    start_at: datetime
    end_at: datetime

    reason: str | None = None
    notes: str | None = None

    @field_validator("reason", "notes")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_at.utcoffset() is None:
            raise ValueError(
                "start_at must include timezone information"
            )

        if self.end_at.utcoffset() is None:
            raise ValueError(
                "end_at must include timezone information"
            )

        if self.end_at <= self.start_at:
            raise ValueError(
                "end_at must be after start_at"
            )

        return self

class AppointmentUpdate(BaseModel):
    patient_id: int | None = Field(
        default=None,
        gt=0
    )

    professional_id: int | None = Field(
        default=None,
        gt=0
    )

    service_id: int | None = Field(
        default=None,
        gt=0
    )

    start_at: datetime | None = None
    end_at: datetime | None = None

    status: AppointmentStatus | None = None

    reason: str | None = None
    notes: str | None = None

    @field_validator("reason", "notes")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("start_at", "end_at")
    @classmethod
    def validate_timezone(
    cls,
    value: datetime | None
    ) -> datetime | None:
        if value is None:
            return None

        if value.utcoffset() is None:
            raise ValueError(
                "Datetime must include timezone information"
            )

        return value
    @field_validator("patient_id", "professional_id")
    @classmethod
    def validate_required_ids(cls, value: int | None) -> int | None:
        if value is None:
            raise ValueError(
                "patient_id and professional_id cannot be null"
            )

        return value

class AppointmentResponse(BaseModel):
    id: int

    patient_id: int
    professional_id: int
    service_id: int | None

    start_at: datetime
    end_at: datetime

    status: AppointmentStatus

    reason: str | None
    notes: str | None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )   

class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    page: int
    page_size: int