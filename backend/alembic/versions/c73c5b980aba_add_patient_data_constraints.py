"""add patient data constraints

Revision ID: c73c5b980aba
Revises: ce3c3d7f3304
Create Date: 2026-09-11 09:59:27.833051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c73c5b980aba'
down_revision: Union[str, Sequence[str], None] = 'ce3c3d7f3304'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Normaliza teléfonos antiguos antes de activar el constraint.
    op.execute(
        """
        UPDATE patients
        SET phone = '+54' || phone
        WHERE phone NOT LIKE '+%'
        """
    )

    op.create_check_constraint(
        "ck_patients_first_name_not_blank",
        "patients",
        "length(trim(first_name)) > 0"
    )

    op.create_check_constraint(
        "ck_patients_last_name_not_blank",
        "patients",
        "length(trim(last_name)) > 0"
    )

    op.create_check_constraint(
        "ck_patients_phone_e164",
        "patients",
        r"phone ~ '^\+[1-9][0-9]{7,14}$'"
    )

    op.create_index(
        op.f("ix_patients_email"),
        "patients",
        ["email"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_patients_email"),
        table_name="patients"
    )

    op.drop_constraint(
        "ck_patients_phone_e164",
        "patients",
        type_="check"
    )

    op.drop_constraint(
        "ck_patients_last_name_not_blank",
        "patients",
        type_="check"
    )

    op.drop_constraint(
        "ck_patients_first_name_not_blank",
        "patients",
        type_="check"
    )