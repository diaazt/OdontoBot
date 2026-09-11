from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

import models
import schemas
from datetime import datetime, timezone

def create_patient(         #crea un paciente en la base de datos 
    db: Session,
    patient: schemas.PatientCreate
) -> models.Patient:

    db_patient = models.Patient(
        **patient.model_dump() #convierte el paciente a un diccionario
    )

    db.add(db_patient)   #agrega el paciente a la base de datos
    db.commit()          #confirma la transaccion
    db.refresh(db_patient) #refresca el paciente en la base de datos

    return db_patient

def get_patient(
    db: Session,
    patient_id: int
) -> models.Patient | None:

    statement = select(models.Patient).where(
        models.Patient.id == patient_id,
        models.Patient.deleted_at.is_(None)
    )

    return db.scalar(statement)

def get_patients(
    db: Session,
    q: str | None = None,
    active: bool | None = None,
    page: int = 1,
    page_size: int = 20
):

    filters = [
        models.Patient.deleted_at.is_(None)
    ]

    if active is not None:
        filters.append(
            models.Patient.active == active
        )

    if q:
        search = f"%{q.strip()}%"

        filters.append(
            or_(
                models.Patient.first_name.ilike(search),
                models.Patient.last_name.ilike(search),
                models.Patient.phone.ilike(search),
                models.Patient.email.ilike(search),
            )
        )

    total_statement = (
        select(func.count())
        .select_from(models.Patient)
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(models.Patient)
        .where(*filters)
        .order_by(
            models.Patient.last_name,
            models.Patient.first_name,
            models.Patient.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    patients = db.scalars(statement).all()

    return patients, total

def find_duplicate_patient(
    db: Session,
    patient: schemas.PatientCreate
) -> models.Patient | None:

    contact_conditions = [
        models.Patient.phone == patient.phone
    ]

    if patient.email is not None:
        contact_conditions.append(
            func.lower(models.Patient.email) == patient.email.lower()
        )

    statement = select(models.Patient).where(
        models.Patient.deleted_at.is_(None),
        func.lower(models.Patient.first_name) == patient.first_name.lower(),
        func.lower(models.Patient.last_name) == patient.last_name.lower(),
        or_(*contact_conditions)
    )

    return db.scalar(statement)

def update_patient(
    db: Session,
    patient_id: int,
    patient_update: schemas.PatientUpdate
) -> models.Patient | None:

    db_patient = get_patient(db, patient_id)

    if db_patient is None:
        return None

    update_data = patient_update.model_dump(exclude_unset=True) #excluye los campos que no se han actualizado

    for field, value in update_data.items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)

    return db_patient

def delete_patient(
    db: Session,
    patient_id: int
) -> models.Patient | None:

    db_patient = get_patient(db, patient_id)

    if db_patient is None:
        return None

    db_patient.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_patient)

    return db_patient

def find_archived_duplicate_patient(
    db: Session,
    patient: schemas.PatientCreate
) -> models.Patient | None:

    contact_conditions = [
        models.Patient.phone == patient.phone
    ]

    if patient.email is not None:
        contact_conditions.append(
            func.lower(models.Patient.email) == patient.email.lower()
        )

    statement = select(models.Patient).where(
        models.Patient.deleted_at.is_not(None),
        func.lower(models.Patient.first_name) == patient.first_name.lower(),
        func.lower(models.Patient.last_name) == patient.last_name.lower(),
        or_(*contact_conditions)
    )

    return db.scalar(statement)

def restore_patient(
    db: Session,
    patient_id: int
) -> models.Patient | None:

    db_patient = db.get(models.Patient, patient_id)

    if db_patient is None:
        return None

    if db_patient.deleted_at is None:
        return db_patient

    db_patient.deleted_at = None

    db.commit()
    db.refresh(db_patient)

    return db_patient