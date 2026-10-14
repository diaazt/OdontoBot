from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

import crud
import schemas
from config import settings


class ProfessionalUnavailableError(Exception):
    pass


class WorkingHoursConflictError(Exception):
    pass


class WorkingHoursInvalidPeriodError(Exception):
    pass

class TimeOffConflictError(Exception):
    pass


class TimeOffAppointmentConflictError(Exception):
    pass


class TimeOffInvalidPeriodError(Exception):
    pass

class InvalidAvailabilityRequestError(Exception):
    pass

def create_working_hours(
    db: Session,
    professional_id: int,
    working_hours: schemas.WorkingHoursCreate
):
    professional = crud.get_active_professional(
        db,
        professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    if working_hours.active:
        overlap = crud.find_overlapping_working_hours(
            db=db,
            professional_id=professional_id,
            weekday=working_hours.weekday,
            start_time=working_hours.start_time,
            end_time=working_hours.end_time
        )

        if overlap is not None:
            raise WorkingHoursConflictError(
                "The working hours overlap with another active period."
            )

    try:
        db_working_hours = crud.create_working_hours(
            db=db,
            professional_id=professional_id,
            working_hours=working_hours
        )

        db.commit()
        db.refresh(db_working_hours)

        return db_working_hours

    except Exception:
        db.rollback()
        raise

def get_professional_working_hours(
    db: Session,
    professional_id: int
):
    professional = crud.get_active_professional(
        db,
        professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    return crud.get_professional_working_hours(
        db,
        professional_id
    )

def update_working_hours(
    db: Session,
    working_hours_id: int,
    working_hours: schemas.WorkingHoursUpdate
):
    db_working_hours = crud.get_working_hours(
        db,
        working_hours_id
    )

    if db_working_hours is None:
        return None

    update_data = working_hours.model_dump(
        exclude_unset=True
    )

    new_weekday = update_data.get(
        "weekday",
        db_working_hours.weekday
    )

    new_start_time = update_data.get(
        "start_time",
        db_working_hours.start_time
    )

    new_end_time = update_data.get(
        "end_time",
        db_working_hours.end_time
    )

    new_active = update_data.get(
        "active",
        db_working_hours.active
    )

    if new_end_time <= new_start_time:
        raise WorkingHoursInvalidPeriodError(
            "end_time must be after start_time."
        )

    if new_active:
        overlap = crud.find_overlapping_working_hours(
            db=db,
            professional_id=db_working_hours.professional_id,
            weekday=new_weekday,
            start_time=new_start_time,
            end_time=new_end_time,
            exclude_working_hours_id=working_hours_id
        )

        if overlap is not None:
            raise WorkingHoursConflictError(
                "The working hours overlap with another active period."
            )

    try:
        db_working_hours = crud.update_working_hours(
            db=db,
            db_working_hours=db_working_hours,
            update_data=update_data
        )

        db.commit()
        db.refresh(db_working_hours)

        return db_working_hours

    except Exception:
        db.rollback()
        raise

def create_time_off(
    db: Session,
    professional_id: int,
    time_off: schemas.TimeOffCreate
):
    professional = crud.get_active_professional(
        db,
        professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    overlapping_time_off = crud.find_overlapping_time_off(
        db=db,
        professional_id=professional_id,
        start_at=time_off.start_at,
        end_at=time_off.end_at
    )

    if overlapping_time_off is not None:
        raise TimeOffConflictError(
            "The time off overlaps with another time off period."
        )

    appointment = crud.find_overlapping_appointment(
        db=db,
        professional_id=professional_id,
        start_at=time_off.start_at,
        end_at=time_off.end_at
    )

    if appointment is not None:
        raise TimeOffAppointmentConflictError(
            "The time off overlaps with an existing appointment."
        )

    try:
        db_time_off = crud.create_time_off(
            db=db,
            professional_id=professional_id,
            time_off=time_off
        )

        db.commit()
        db.refresh(db_time_off)

        return db_time_off

    except Exception:
        db.rollback()
        raise

def get_professional_time_off(
    db: Session,
    professional_id: int
):
    professional = crud.get_active_professional(
        db,
        professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    return crud.get_professional_time_off(
        db,
        professional_id
    )

def update_time_off(
    db: Session,
    time_off_id: int,
    time_off: schemas.TimeOffUpdate
):
    db_time_off = crud.get_time_off(
        db,
        time_off_id
    )

    if db_time_off is None:
        return None

    update_data = time_off.model_dump(
        exclude_unset=True
    )

    new_start_at = update_data.get(
        "start_at",
        db_time_off.start_at
    )

    new_end_at = update_data.get(
        "end_at",
        db_time_off.end_at
    )

    if new_end_at <= new_start_at:
        raise TimeOffInvalidPeriodError(
            "end_at must be after start_at."
        )

    overlapping_time_off = crud.find_overlapping_time_off(
        db=db,
        professional_id=db_time_off.professional_id,
        start_at=new_start_at,
        end_at=new_end_at,
        exclude_time_off_id=time_off_id
    )

    if overlapping_time_off is not None:
        raise TimeOffConflictError(
            "The time off overlaps with another time off period."
        )

    appointment = crud.find_overlapping_appointment(
        db=db,
        professional_id=db_time_off.professional_id,
        start_at=new_start_at,
        end_at=new_end_at
    )

    if appointment is not None:
        raise TimeOffAppointmentConflictError(
            "The time off overlaps with an existing appointment."
        )

    try:
        db_time_off = crud.update_time_off(
            db=db,
            db_time_off=db_time_off,
            update_data=update_data
        )

        db.commit()
        db.refresh(db_time_off)

        return db_time_off

    except Exception:
        db.rollback()
        raise

def delete_time_off(
    db: Session,
    time_off_id: int
):
    return crud.delete_time_off(
        db,
        time_off_id
    )

def periods_overlap(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime
) -> bool:
    return start_a < end_b and end_a > start_b

def get_available_slots(
    db: Session,
    professional_id: int,
    target_date: date,
    duration_minutes: int,
    slot_step_minutes: int = 15
):
    if duration_minutes <= 0:
        raise InvalidAvailabilityRequestError(
            "duration_minutes must be greater than zero."
        )

    if slot_step_minutes <= 0:
        raise InvalidAvailabilityRequestError(
            "slot_step_minutes must be greater than zero."
        )

    professional = crud.get_active_professional(
        db,
        professional_id
    )

    if professional is None:
        raise ProfessionalUnavailableError(
            "Professional does not exist or is not active."
        )

    clinic_timezone = ZoneInfo(
        settings.clinic_timezone
    )

    day_start = datetime.combine(
        target_date,
        time.min,
        tzinfo=clinic_timezone
    )

    day_end = day_start + timedelta(days=1)

    weekday = target_date.weekday()

    working_hours = (
        crud.get_active_working_hours_for_weekday(
            db=db,
            professional_id=professional_id,
            weekday=weekday
        )
    )

    if not working_hours:
        return []

    appointments = crud.get_blocking_appointments(
        db=db,
        professional_id=professional_id,
        start_at=day_start,
        end_at=day_end
    )

    time_off_periods = crud.get_time_off_in_range(
        db=db,
        professional_id=professional_id,
        start_at=day_start,
        end_at=day_end
    )

    duration = timedelta(
        minutes=duration_minutes
    )

    step = timedelta(
        minutes=slot_step_minutes
    )

    available_slots = []

    for working_period in working_hours:
        period_start = datetime.combine(
            target_date,
            working_period.start_time,
            tzinfo=clinic_timezone
        )

        period_end = datetime.combine(
            target_date,
            working_period.end_time,
            tzinfo=clinic_timezone
        )

        candidate_start = period_start

        while candidate_start + duration <= period_end:
            candidate_end = (
                candidate_start + duration
            )

            appointment_conflict = any(
                periods_overlap(
                    candidate_start,
                    candidate_end,
                    appointment.start_at,
                    appointment.end_at
                )
                for appointment in appointments
            )

            time_off_conflict = any(
                periods_overlap(
                    candidate_start,
                    candidate_end,
                    time_off.start_at,
                    time_off.end_at
                )
                for time_off in time_off_periods
            )

            if (
                not appointment_conflict
                and not time_off_conflict
            ):
                available_slots.append(
                    {
                        "start_at": candidate_start,
                        "end_at": candidate_end
                    }
                )

            candidate_start += step

    return available_slots