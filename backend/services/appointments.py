from sqlalchemy.orm import Session

import crud
import schemas


class PatientUnavailableError(Exception):
    pass


class ProfessionalUnavailableError(Exception):
    pass


class ServiceUnavailableError(Exception):
    pass


class AppointmentConflictError(Exception):
    pass

class AppointmentInvalidPeriodError(Exception):
    pass

def create_appointment(
    db: Session,
    appointment: schemas.AppointmentCreate
):
    patient = crud.get_active_patient(
        db,
        appointment.patient_id
    )

    if patient is None:
        raise PatientUnavailableError(
            "Patient does not exist or is not active."
        )

    professional = crud.get_active_professional(
        db,
        appointment.professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    if appointment.service_id is not None:
        service = crud.get_active_service(
            db,
            appointment.service_id
        )

        if service is None:
            raise ServiceUnavailableError(
                "Service does not exist or is not active."
            )

    overlap = crud.find_overlapping_appointment(
        db=db,
        professional_id=appointment.professional_id,
        start_at=appointment.start_at,
        end_at=appointment.end_at
    )

    if overlap is not None:
        raise AppointmentConflictError(
            "The professional already has an appointment "
            "during this time range."
        )

    try:
        db_appointment = crud.create_appointment(
            db,
            appointment
        )

        db.commit()
        db.refresh(db_appointment)

        return db_appointment

    except Exception:
        db.rollback()
        raise

def get_appointment(
    db: Session,
    appointment_id: int
):
    return crud.get_appointment(
        db,
        appointment_id
    )


def get_appointments(
    db: Session,
    patient_id: int | None = None,
    professional_id: int | None = None,
    status: str | None = None,
    start_from=None,
    start_until=None,
    page: int = 1,
    page_size: int = 20
):
    return crud.get_appointments(
        db=db,
        patient_id=patient_id,
        professional_id=professional_id,
        status=status,
        start_from=start_from,
        start_until=start_until,
        page=page,
        page_size=page_size
    )

def delete_appointment(
    db: Session,
    appointment_id: int
):
    return crud.delete_appointment(
        db,
        appointment_id
    )

def restore_appointment(
    db: Session,
    appointment_id: int
):
    db_appointment = crud.get_appointment_including_deleted(
        db,
        appointment_id
    )

    if db_appointment is None:
        return None

    if db_appointment.deleted_at is None:
        return db_appointment

    if db_appointment.status not in [
        "cancelled",
        "no_show"
    ]:
        overlap = crud.find_overlapping_appointment(
            db=db,
            professional_id=db_appointment.professional_id,
            start_at=db_appointment.start_at,
            end_at=db_appointment.end_at,
            exclude_appointment_id=appointment_id
        )

        if overlap is not None:
            raise AppointmentConflictError(
                "The appointment cannot be restored because "
                "the professional already has another appointment "
                "during this time range."
            )

    try:
        db_appointment.deleted_at = None

        db.commit()
        db.refresh(db_appointment)

        return db_appointment

    except Exception:
        db.rollback()
        raise

def update_appointment(
    db: Session,
    appointment_id: int,
    appointment: schemas.AppointmentUpdate
):
    db_appointment = crud.get_appointment(
        db,
        appointment_id
    )

    if db_appointment is None:
        return None

    update_data = appointment.model_dump(
        exclude_unset=True
    )

    new_patient_id = update_data.get(
        "patient_id",
        db_appointment.patient_id
    )

    new_professional_id = update_data.get(
        "professional_id",
        db_appointment.professional_id
    )

    new_service_id = update_data.get(
        "service_id",
        db_appointment.service_id
    )

    new_start_at = update_data.get(
        "start_at",
        db_appointment.start_at
    )

    new_end_at = update_data.get(
        "end_at",
        db_appointment.end_at
    )

    new_status = update_data.get(
        "status",
        db_appointment.status
    )

    if new_end_at <= new_start_at:
        raise AppointmentInvalidPeriodError(
            "end_at must be after start_at."
        )

    patient = crud.get_active_patient(
        db,
        new_patient_id
    )

    if patient is None:
        raise PatientUnavailableError(
            "Patient does not exist or is not active."
        )

    professional = crud.get_active_professional(
        db,
        new_professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    if new_service_id is not None:
        service = crud.get_active_service(
            db,
            new_service_id
        )

        if service is None:
            raise ServiceUnavailableError(
                "Service does not exist or is not active."
            )

    if new_status not in [
        "cancelled",
        "no_show"
    ]:
        overlap = crud.find_overlapping_appointment(
            db=db,
            professional_id=new_professional_id,
            start_at=new_start_at,
            end_at=new_end_at,
            exclude_appointment_id=appointment_id
        )

        if overlap is not None:
            raise AppointmentConflictError(
                "The professional already has an appointment "
                "during this time range."
            )

    try:
        db_appointment = crud.update_appointment(
            db=db,
            db_appointment=db_appointment,
            update_data=update_data
        )

        db.commit()
        db.refresh(db_appointment)

        return db_appointment

    except Exception:
        db.rollback()
        raise