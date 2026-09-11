import pytest
from pydantic import ValidationError

import schemas


def test_create_patient_normalizes_data():
    patient = schemas.PatientCreate(
        first_name="   Carlos   ",
        last_name="   Perez   ",
        phone="+54 9 11 2345 6789",
        email="CARLOS@GMAIL.COM"
    )

    assert patient.first_name == "Carlos"
    assert patient.last_name == "Perez"
    assert patient.phone == "+5491123456789"
    assert patient.email == "carlos@gmail.com"


def test_create_patient_rejects_invalid_email():
    with pytest.raises(ValidationError):
        schemas.PatientCreate(
            first_name="Carlos",
            last_name="Perez",
            phone="+54 9 11 2345 6789",
            email="banana"
        )


def test_create_patient_rejects_invalid_phone():
    with pytest.raises(ValidationError):
        schemas.PatientCreate(
            first_name="Carlos",
            last_name="Perez",
            phone="hola",
            email="carlos@gmail.com"
        )


def test_create_patient_rejects_blank_name():
    with pytest.raises(ValidationError):
        schemas.PatientCreate(
            first_name="   ",
            last_name="Perez",
            phone="+54 9 11 2345 6789",
            email="carlos@gmail.com"
        )