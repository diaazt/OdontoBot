from datetime import datetime, time

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func, Numeric, ForeignKey, text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

from decimal import Decimal


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    phone: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    __table_args__ = (
    CheckConstraint(
        "length(trim(first_name)) > 0",
        name="ck_patients_first_name_not_blank"
    ),
    CheckConstraint(
        "length(trim(last_name)) > 0",
        name="ck_patients_last_name_not_blank"
    ),
    CheckConstraint(
        r"phone ~ '^\+[1-9][0-9]{7,14}$'",
        name="ck_patients_phone_e164"
    ),
    )
    updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(   
    DateTime(timezone=True),
    nullable=True
    )
    appointments: Mapped[list["Appointment"]] = relationship(
    back_populates="patient"
    )

class Professional(Base):
    __tablename__ = "professionals"

    __table_args__ = (
        CheckConstraint(
            "length(trim(first_name)) > 0",
            name="ck_professionals_first_name_not_blank"
        ),
        CheckConstraint(
            "length(trim(last_name)) > 0",
            name="ck_professionals_last_name_not_blank"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    specialty: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    license_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    appointments: Mapped[list["Appointment"]] = relationship(
    back_populates="professional"
    )
    working_hours: Mapped[list["ProfessionalWorkingHours"]] = relationship(
    back_populates="professional"
    )
    time_off_periods: Mapped[list["ProfessionalTimeOff"]] = relationship(
    back_populates="professional"
)

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import relationship


class Service(Base):
    __tablename__ = "services"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_services_name_not_blank"
        ),
        CheckConstraint(
            "estimated_duration_minutes > 0",
            name="ck_services_duration_positive"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    estimated_duration_minutes: Mapped[int]

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    prices: Mapped[list["ServicePrice"]] = relationship(
        back_populates="service"
    )
    prices: Mapped[list["ServicePrice"]] = relationship(
    back_populates="service"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
    back_populates="service"
    )


class ServicePrice(Base):
    __tablename__ = "service_prices"

    __table_args__ = (
    CheckConstraint(
        "amount >= 0",
        name="ck_service_prices_amount_not_negative"
    ),
    CheckConstraint(
        "valid_until IS NULL OR valid_until > valid_from",
        name="ck_service_prices_valid_period"
    ),
    Index(
        "uq_service_prices_current_per_service",
        "service_id",
        unique=True,
        postgresql_where=text("valid_until IS NULL")
    ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"),
        index=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    service: Mapped["Service"] = relationship(
        back_populates="prices"
    )

class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "end_at > start_at",
            name="ck_appointments_end_after_start"
        ),
        CheckConstraint(
            """
            status IN (
                'scheduled',
                'confirmed',
                'completed',
                'cancelled',
                'no_show'
            )
            """,
            name="ck_appointments_status_valid"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="RESTRICT"
        ),
        index=True
    )

    professional_id: Mapped[int] = mapped_column(
        ForeignKey(
            "professionals.id",
            ondelete="RESTRICT"
        ),
        index=True
    )

    service_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="RESTRICT"
        ),
        nullable=True,
        index=True
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="scheduled",
        index=True
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="appointments"
    )

    professional: Mapped["Professional"] = relationship(
        back_populates="appointments"
    )

    service: Mapped["Service | None"] = relationship(
        back_populates="appointments"
    )

class ProfessionalWorkingHours(Base):
    __tablename__ = "professional_working_hours"

    __table_args__ = (
        CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="ck_working_hours_weekday_valid"
        ),
        CheckConstraint(
            "end_time > start_time",
            name="ck_working_hours_end_after_start"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    professional_id: Mapped[int] = mapped_column(
        ForeignKey(
            "professionals.id",
            ondelete="RESTRICT"
        ),
        index=True
    )

    weekday: Mapped[int] = mapped_column(
        index=True
    )

    start_time: Mapped[time]

    end_time: Mapped[time]

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    professional: Mapped["Professional"] = relationship(
        back_populates="working_hours"
    )

class ProfessionalTimeOff(Base):
    __tablename__ = "professional_time_off"

    __table_args__ = (
        CheckConstraint(
            "end_at > start_at",
            name="ck_professional_time_off_end_after_start"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    professional_id: Mapped[int] = mapped_column(
        ForeignKey(
            "professionals.id",
            ondelete="RESTRICT"
        ),
        index=True
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    professional: Mapped["Professional"] = relationship(
        back_populates="time_off_periods"
    )

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'secretary', 'professional')",
            name="ck_users_role_valid"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    role: Mapped[str] = mapped_column(
        String(30),
        index=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )