from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

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

def get_active_patient(
    db: Session,
    patient_id: int
):
    statement = (
        select(models.Patient)
        .where(
            models.Patient.id == patient_id,
            models.Patient.deleted_at.is_(None),
            models.Patient.active.is_(True)
        )
    )

    return db.scalar(statement)


def get_active_professional(
    db: Session,
    professional_id: int
):
    statement = (
        select(models.Professional)
        .where(
            models.Professional.id == professional_id,
            models.Professional.deleted_at.is_(None),
            models.Professional.active.is_(True)
        )
    )

    return db.scalar(statement)


def get_active_service(
    db: Session,
    service_id: int
):
    statement = (
        select(models.Service)
        .where(
            models.Service.id == service_id,
            models.Service.deleted_at.is_(None),
            models.Service.active.is_(True)
        )
    )

    return db.scalar(statement)

def create_professional(
    db: Session,
    professional: schemas.ProfessionalCreate
) -> models.Professional:

    db_professional = models.Professional(
        **professional.model_dump()
    )

    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)

    return db_professional


def get_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    statement = select(models.Professional).where(
        models.Professional.id == professional_id,
        models.Professional.deleted_at.is_(None)
    )

    return db.scalar(statement)


def get_professionals(
    db: Session,
    q: str | None = None,
    active: bool | None = None,
    specialty: str | None = None,
    page: int = 1,
    page_size: int = 20
):

    filters = [
        models.Professional.deleted_at.is_(None)
    ]

    if active is not None:
        filters.append(
            models.Professional.active == active
        )

    if specialty:
        filters.append(
            models.Professional.specialty.ilike(
                f"%{specialty.strip()}%"
            )
        )

    if q:
        search = f"%{q.strip()}%"

        filters.append(
            or_(
                models.Professional.first_name.ilike(search),
                models.Professional.last_name.ilike(search),
                models.Professional.specialty.ilike(search),
                models.Professional.license_number.ilike(search),
                models.Professional.phone.ilike(search),
                models.Professional.email.ilike(search),
            )
        )

    total_statement = (
        select(func.count())
        .select_from(models.Professional)
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(models.Professional)
        .where(*filters)
        .order_by(
            models.Professional.last_name,
            models.Professional.first_name,
            models.Professional.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    professionals = db.scalars(statement).all()

    return professionals, total

def update_professional(
    db: Session,
    professional_id: int,
    professional_update: schemas.ProfessionalUpdate
) -> models.Professional | None:

    db_professional = get_professional(
        db,
        professional_id
    )

    if db_professional is None:
        return None

    update_data = professional_update.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(db_professional, field, value)

    db.commit()
    db.refresh(db_professional)

    return db_professional

def delete_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    db_professional = get_professional(
        db,
        professional_id
    )

    if db_professional is None:
        return None

    db_professional.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_professional)

    return db_professional

def find_duplicate_professional(
    db: Session,
    professional: schemas.ProfessionalCreate
) -> models.Professional | None:

    conditions = []

    if professional.license_number is not None:
        conditions.append(
            func.lower(models.Professional.license_number)
            == professional.license_number.lower()
        )

    if professional.email is not None:
        conditions.append(
            func.lower(models.Professional.email)
            == professional.email.lower()
        )

    if professional.phone is not None:
        conditions.append(
            models.Professional.phone == professional.phone
        )

    if not conditions:
        return None

    statement = select(models.Professional).where(
        models.Professional.deleted_at.is_(None),
        func.lower(models.Professional.first_name)
        == professional.first_name.lower(),
        func.lower(models.Professional.last_name)
        == professional.last_name.lower(),
        or_(*conditions)
    )

    return db.scalar(statement)

def find_archived_duplicate_professional(
    db: Session,
    professional: schemas.ProfessionalCreate
) -> models.Professional | None:

    conditions = []

    if professional.license_number is not None:
        conditions.append(
            func.lower(models.Professional.license_number)
            == professional.license_number.lower()
        )

    if professional.email is not None:
        conditions.append(
            func.lower(models.Professional.email)
            == professional.email.lower()
        )

    if professional.phone is not None:
        conditions.append(
            models.Professional.phone == professional.phone
        )

    if not conditions:
        return None

    statement = select(models.Professional).where(
        models.Professional.deleted_at.is_not(None),
        func.lower(models.Professional.first_name)
        == professional.first_name.lower(),
        func.lower(models.Professional.last_name)
        == professional.last_name.lower(),
        or_(*conditions)
    )

    return db.scalar(statement)

def restore_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    db_professional = db.get(
        models.Professional,
        professional_id
    )

    if db_professional is None:
        return None

    if db_professional.deleted_at is None:
        return db_professional

    db_professional.deleted_at = None

    db.commit()
    db.refresh(db_professional)

    return db_professional

def create_service(
    db: Session,
    service: schemas.ServiceCreate
):
    service_data = service.model_dump(
        exclude={"initial_price"}
    )

    db_service = models.Service(
        **service_data
    )

    db.add(db_service)

    # Envía el INSERT a PostgreSQL sin confirmar todavía
    # para obtener, entre otras cosas, el ID.
    db.flush()

    return db_service


def create_service_price(
    db: Session,
    service_id: int,
    amount,
    valid_from: datetime | None = None
):
    price_data = {
        "service_id": service_id,
        "amount": amount
    }

    if valid_from is not None:
        price_data["valid_from"] = valid_from

    db_price = models.ServicePrice(
        **price_data
    )

    db.add(db_price)
    db.flush()

    return db_price

def get_service(
    db: Session,
    service_id: int
):
    statement = (
        select(models.Service)
        .options(
            selectinload(models.Service.prices)
        )
        .where(
            models.Service.id == service_id,
            models.Service.deleted_at.is_(None)
        )
    )

    return db.scalar(statement)


def get_services(
    db: Session,
    q: str | None = None,
    active: bool | None = None,
    page: int = 1,
    page_size: int = 20
):
    filters = [
        models.Service.deleted_at.is_(None)
    ]

    if active is not None:
        filters.append(
            models.Service.active == active
        )

    if q:
        search = f"%{q.strip()}%"

        filters.append(
            or_(
                models.Service.name.ilike(search),
                models.Service.description.ilike(search)
            )
        )

    total_statement = (
        select(func.count())
        .select_from(models.Service)
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(models.Service)
        .options(
            selectinload(models.Service.prices)
        )
        .where(*filters)
        .order_by(
            models.Service.name,
            models.Service.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    services = db.scalars(statement).all()

    return services, total

def update_service(
    db: Session,
    service_id: int,
    service: schemas.ServiceUpdate
):
    db_service = get_service(
        db,
        service_id
    )

    if db_service is None:
        return None

    update_data = service.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            db_service,
            field,
            value
        )

    db.commit()
    db.refresh(db_service)

    return db_service

def delete_service(
    db: Session,
    service_id: int
):
    db_service = get_service(
        db,
        service_id
    )

    if db_service is None:
        return None

    db_service.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(db_service)

    return db_service

def restore_service(
    db: Session,
    service_id: int
):
    db_service = db.get(
        models.Service,
        service_id
    )

    if db_service is None:
        return None

    if db_service.deleted_at is None:
        return db_service

    db_service.deleted_at = None

    db.commit()
    db.refresh(db_service)

    return db_service

def get_service_for_update(
    db: Session,
    service_id: int
):
    statement = (
        select(models.Service)
        .where(
            models.Service.id == service_id,
            models.Service.deleted_at.is_(None)
        )
        .with_for_update()
    )

    return db.scalar(statement)

def get_current_service_price(
    db: Session,
    service_id: int
):
    statement = (
        select(models.ServicePrice)
        .where(
            models.ServicePrice.service_id == service_id,
            models.ServicePrice.valid_until.is_(None)
        )
    )

    return db.scalar(statement)

def close_service_price(
    db: Session,
    price: models.ServicePrice,
    valid_until: datetime
):
    price.valid_until = valid_until

    db.flush()

    return price

def find_duplicate_service(
    db: Session,
    service: schemas.ServiceCreate
):
    statement = (
        select(models.Service)
        .where(
            models.Service.deleted_at.is_(None),
            func.lower(models.Service.name) == service.name.lower()
        )
    )

    return db.scalar(statement)


def find_archived_duplicate_service(
    db: Session,
    service: schemas.ServiceCreate
):
    statement = (
        select(models.Service)
        .where(
            models.Service.deleted_at.is_not(None),
            func.lower(models.Service.name) == service.name.lower()
        )
    )

    return db.scalar(statement)

def create_appointment(
    db: Session,
    appointment: schemas.AppointmentCreate
):
    db_appointment = models.Appointment(
        **appointment.model_dump()
    )

    db.add(db_appointment)
    db.flush()

    return db_appointment

def get_appointment(
    db: Session,
    appointment_id: int
):
    statement = (
        select(models.Appointment)
        .where(
            models.Appointment.id == appointment_id,
            models.Appointment.deleted_at.is_(None)
        )
    )

    return db.scalar(statement)

def find_overlapping_appointment(
    db: Session,
    professional_id: int,
    start_at: datetime,
    end_at: datetime,
    exclude_appointment_id: int | None = None
):
    statement = (
        select(models.Appointment)
        .where(
            models.Appointment.professional_id == professional_id,
            models.Appointment.deleted_at.is_(None),
            models.Appointment.status.notin_(
                ["cancelled", "no_show"]
            ),
            models.Appointment.start_at < end_at,
            models.Appointment.end_at > start_at
        )
    )

    if exclude_appointment_id is not None:
        statement = statement.where(
            models.Appointment.id != exclude_appointment_id
        )

    return db.scalar(statement)



def update_appointment(
    db: Session,
    db_appointment: models.Appointment,
    update_data: dict
):
    for field, value in update_data.items():
        setattr(
            db_appointment,
            field,
            value
        )

    db.flush()

    return db_appointment



def get_appointments(
    db: Session,
    patient_id: int | None = None,
    professional_id: int | None = None,
    status: str | None = None,
    start_from: datetime | None = None,
    start_until: datetime | None = None,
    page: int = 1,
    page_size: int = 20
):
    filters = [
        models.Appointment.deleted_at.is_(None)
    ]

    if patient_id is not None:
        filters.append(
            models.Appointment.patient_id == patient_id
        )

    if professional_id is not None:
        filters.append(
            models.Appointment.professional_id == professional_id
        )

    if status is not None:
        filters.append(
            models.Appointment.status == status
        )

    if start_from is not None:
        filters.append(
            models.Appointment.start_at >= start_from
        )

    if start_until is not None:
        filters.append(
            models.Appointment.start_at < start_until
        )

    total_statement = (
        select(func.count())
        .select_from(models.Appointment)
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(models.Appointment)
        .where(*filters)
        .order_by(
            models.Appointment.start_at,
            models.Appointment.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    appointments = db.scalars(statement).all()

    return appointments, total

def delete_appointment(
    db: Session,
    appointment_id: int
):
    db_appointment = get_appointment(
        db,
        appointment_id
    )

    if db_appointment is None:
        return None

    db_appointment.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(db_appointment)

    return db_appointment

def get_appointment_including_deleted(
    db: Session,
    appointment_id: int
):
    return db.get(
        models.Appointment,
        appointment_id
    )

def create_working_hours(
    db: Session,
    professional_id: int,
    working_hours: schemas.WorkingHoursCreate
):
    db_working_hours = models.ProfessionalWorkingHours(
        professional_id=professional_id,
        **working_hours.model_dump()
    )

    db.add(db_working_hours)
    db.flush()

    return db_working_hours


def get_working_hours(
    db: Session,
    working_hours_id: int
):
    return db.get(
        models.ProfessionalWorkingHours,
        working_hours_id
    )


def get_professional_working_hours(
    db: Session,
    professional_id: int
):
    statement = (
        select(models.ProfessionalWorkingHours)
        .where(
            models.ProfessionalWorkingHours.professional_id
            == professional_id
        )
        .order_by(
            models.ProfessionalWorkingHours.weekday,
            models.ProfessionalWorkingHours.start_time
        )
    )

    return db.scalars(statement).all()


def find_overlapping_working_hours(
    db: Session,
    professional_id: int,
    weekday: int,
    start_time,
    end_time,
    exclude_working_hours_id: int | None = None
):
    statement = (
        select(models.ProfessionalWorkingHours)
        .where(
            models.ProfessionalWorkingHours.professional_id
            == professional_id,
            models.ProfessionalWorkingHours.weekday
            == weekday,
            models.ProfessionalWorkingHours.active.is_(True),
            models.ProfessionalWorkingHours.start_time
            < end_time,
            models.ProfessionalWorkingHours.end_time
            > start_time
        )
    )

    if exclude_working_hours_id is not None:
        statement = statement.where(
            models.ProfessionalWorkingHours.id
            != exclude_working_hours_id
        )

    return db.scalar(statement)


def update_working_hours(
    db: Session,
    db_working_hours: models.ProfessionalWorkingHours,
    update_data: dict
):
    for field, value in update_data.items():
        setattr(
            db_working_hours,
            field,
            value
        )

    db.flush()

    return db_working_hours

def create_time_off(
    db: Session,
    professional_id: int,
    time_off: schemas.TimeOffCreate
):
    db_time_off = models.ProfessionalTimeOff(
        professional_id=professional_id,
        **time_off.model_dump()
    )

    db.add(db_time_off)
    db.flush()

    return db_time_off


def get_time_off(
    db: Session,
    time_off_id: int
):
    statement = (
        select(models.ProfessionalTimeOff)
        .where(
            models.ProfessionalTimeOff.id == time_off_id,
            models.ProfessionalTimeOff.deleted_at.is_(None)
        )
    )

    return db.scalar(statement)


def get_professional_time_off(
    db: Session,
    professional_id: int
):
    statement = (
        select(models.ProfessionalTimeOff)
        .where(
            models.ProfessionalTimeOff.professional_id
            == professional_id,
            models.ProfessionalTimeOff.deleted_at.is_(None)
        )
        .order_by(
            models.ProfessionalTimeOff.start_at,
            models.ProfessionalTimeOff.id
        )
    )

    return db.scalars(statement).all()


def find_overlapping_time_off(
    db: Session,
    professional_id: int,
    start_at: datetime,
    end_at: datetime,
    exclude_time_off_id: int | None = None
):
    statement = (
        select(models.ProfessionalTimeOff)
        .where(
            models.ProfessionalTimeOff.professional_id
            == professional_id,
            models.ProfessionalTimeOff.deleted_at.is_(None),
            models.ProfessionalTimeOff.start_at < end_at,
            models.ProfessionalTimeOff.end_at > start_at
        )
    )

    if exclude_time_off_id is not None:
        statement = statement.where(
            models.ProfessionalTimeOff.id
            != exclude_time_off_id
        )

    return db.scalar(statement)


def update_time_off(
    db: Session,
    db_time_off: models.ProfessionalTimeOff,
    update_data: dict
):
    for field, value in update_data.items():
        setattr(
            db_time_off,
            field,
            value
        )

    db.flush()

    return db_time_off


def delete_time_off(
    db: Session,
    time_off_id: int
):
    db_time_off = get_time_off(
        db,
        time_off_id
    )

    if db_time_off is None:
        return None

    db_time_off.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(db_time_off)

    return db_time_off

def get_active_working_hours_for_weekday(
    db: Session,
    professional_id: int,
    weekday: int
):
    statement = (
        select(models.ProfessionalWorkingHours)
        .where(
            models.ProfessionalWorkingHours.professional_id
            == professional_id,
            models.ProfessionalWorkingHours.weekday
            == weekday,
            models.ProfessionalWorkingHours.active.is_(True)
        )
        .order_by(
            models.ProfessionalWorkingHours.start_time
        )
    )

    return db.scalars(statement).all()


def get_blocking_appointments(
    db: Session,
    professional_id: int,
    start_at: datetime,
    end_at: datetime
):
    statement = (
        select(models.Appointment)
        .where(
            models.Appointment.professional_id
            == professional_id,
            models.Appointment.deleted_at.is_(None),
            models.Appointment.status.notin_(
                ["cancelled", "no_show"]
            ),
            models.Appointment.start_at < end_at,
            models.Appointment.end_at > start_at
        )
        .order_by(models.Appointment.start_at)
    )

    return db.scalars(statement).all()


def get_time_off_in_range(
    db: Session,
    professional_id: int,
    start_at: datetime,
    end_at: datetime
):
    statement = (
        select(models.ProfessionalTimeOff)
        .where(
            models.ProfessionalTimeOff.professional_id
            == professional_id,
            models.ProfessionalTimeOff.deleted_at.is_(None),
            models.ProfessionalTimeOff.start_at < end_at,
            models.ProfessionalTimeOff.end_at > start_at
        )
        .order_by(models.ProfessionalTimeOff.start_at)
    )

    return db.scalars(statement).all()