from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import schemas
from database import get_db
from services import availability as availability_service


router = APIRouter(
    prefix="/availability",
    tags=["Availability"]
)


@router.post(
    "/professionals/{professional_id}/working-hours",
    response_model=schemas.WorkingHoursResponse,
    status_code=201
)
def create_working_hours(
    professional_id: int,
    working_hours: schemas.WorkingHoursCreate,
    db: Session = Depends(get_db)
):
    try:
        return availability_service.create_working_hours(
            db=db,
            professional_id=professional_id,
            working_hours=working_hours
        )

    except availability_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.WorkingHoursConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.get(
    "/professionals/{professional_id}/working-hours",
    response_model=list[schemas.WorkingHoursResponse]
)
def get_working_hours(
    professional_id: int,
    db: Session = Depends(get_db)
):
    try:
        return availability_service.get_professional_working_hours(
            db=db,
            professional_id=professional_id
        )

    except availability_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


@router.patch(
    "/working-hours/{working_hours_id}",
    response_model=schemas.WorkingHoursResponse
)
def update_working_hours(
    working_hours_id: int,
    working_hours: schemas.WorkingHoursUpdate,
    db: Session = Depends(get_db)
):
    try:
        result = availability_service.update_working_hours(
            db=db,
            working_hours_id=working_hours_id,
            working_hours=working_hours
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Working hours not found"
            )

        return result

    except availability_service.WorkingHoursConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.WorkingHoursInvalidPeriodError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@router.post(
    "/professionals/{professional_id}/time-off",
    response_model=schemas.TimeOffResponse,
    status_code=201
)
def create_time_off(
    professional_id: int,
    time_off: schemas.TimeOffCreate,
    db: Session = Depends(get_db)
):
    try:
        return availability_service.create_time_off(
            db=db,
            professional_id=professional_id,
            time_off=time_off
        )

    except availability_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.TimeOffConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.TimeOffAppointmentConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.get(
    "/professionals/{professional_id}/time-off",
    response_model=list[schemas.TimeOffResponse]
)
def get_time_off(
    professional_id: int,
    db: Session = Depends(get_db)
):
    try:
        return availability_service.get_professional_time_off(
            db=db,
            professional_id=professional_id
        )

    except availability_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


@router.patch(
    "/time-off/{time_off_id}",
    response_model=schemas.TimeOffResponse
)
def update_time_off(
    time_off_id: int,
    time_off: schemas.TimeOffUpdate,
    db: Session = Depends(get_db)
):
    try:
        result = availability_service.update_time_off(
            db=db,
            time_off_id=time_off_id,
            time_off=time_off
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Time off not found"
            )

        return result

    except availability_service.TimeOffConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.TimeOffAppointmentConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except availability_service.TimeOffInvalidPeriodError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@router.delete(
    "/time-off/{time_off_id}",
    response_model=schemas.TimeOffResponse
)
def delete_time_off(
    time_off_id: int,
    db: Session = Depends(get_db)
):
    result = availability_service.delete_time_off(
        db=db,
        time_off_id=time_off_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Time off not found"
        )

    return result


@router.get(
    "/professionals/{professional_id}/slots",
    response_model=schemas.AvailabilityResponse
)
def get_available_slots(
    professional_id: int,
    target_date: date,
    duration_minutes: int = Query(gt=0, le=480),
    slot_step_minutes: int = Query(
        default=15,
        gt=0,
        le=120
    ),
    db: Session = Depends(get_db)
):
    try:
        slots = availability_service.get_available_slots(
            db=db,
            professional_id=professional_id,
            target_date=target_date,
            duration_minutes=duration_minutes,
            slot_step_minutes=slot_step_minutes
        )

        return {
            "professional_id": professional_id,
            "date": target_date,
            "duration_minutes": duration_minutes,
            "slot_step_minutes": slot_step_minutes,
            "slots": slots
        }

    except availability_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except availability_service.InvalidAvailabilityRequestError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )