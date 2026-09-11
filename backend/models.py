from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


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