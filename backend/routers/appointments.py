from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import schemas
from database import get_db
from services import appointments as appointment_service


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post(
    "/",
    response_model=schemas.AppointmentResponse,
    status_code=201
)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db)
):
    try:
        return appointment_service.create_appointment(
            db,
            appointment
        )

    except appointment_service.PatientUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.ServiceUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.AppointmentConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.get(
    "/",
    response_model=schemas.AppointmentListResponse
)
def get_appointments(
    patient_id: int | None = Query(
        default=None,
        gt=0
    ),
    professional_id: int | None = Query(
        default=None,
        gt=0
    ),
    status: schemas.AppointmentStatus | None = None,
    start_from: datetime | None = None,
    start_until: datetime | None = None,
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
):
    appointments, total = appointment_service.get_appointments(
        db=db,
        patient_id=patient_id,
        professional_id=professional_id,
        status=status,
        start_from=start_from,
        start_until=start_until,
        page=page,
        page_size=page_size
    )

    return {
        "items": appointments,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get(
    "/{appointment_id}",
    response_model=schemas.AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    appointment = appointment_service.get_appointment(
        db,
        appointment_id
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


@router.patch(
    "/{appointment_id}",
    response_model=schemas.AppointmentResponse
)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_appointment = appointment_service.update_appointment(
            db=db,
            appointment_id=appointment_id,
            appointment=appointment
        )

        if updated_appointment is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found"
            )

        return updated_appointment

    except appointment_service.PatientUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.ProfessionalUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.ServiceUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.AppointmentConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except appointment_service.AppointmentInvalidPeriodError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@router.delete(
    "/{appointment_id}",
    response_model=schemas.AppointmentResponse
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    appointment = appointment_service.delete_appointment(
        db,
        appointment_id
    )

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


@router.post(
    "/{appointment_id}/restore",
    response_model=schemas.AppointmentResponse
)
def restore_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    try:
        appointment = appointment_service.restore_appointment(
            db,
            appointment_id
        )

        if appointment is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found"
            )

        return appointment

    except appointment_service.AppointmentConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )