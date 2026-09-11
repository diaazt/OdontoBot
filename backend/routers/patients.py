from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from services import patients as patient_service
import crud
import schemas
from database import get_db


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=schemas.PatientResponse,
    status_code=201
)

def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    try:
        return patient_service.create_patient(db, patient)

    except patient_service.PatientDuplicateError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )
    except patient_service.PatientArchivedError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "PATIENT_ARCHIVED",
                "message": "A matching archived patient already exists.",
                "patient_id": exc.patient_id
            }
        )

@router.get(
    "/",
    response_model=schemas.PatientListResponse
)
def get_patients(
    q: str | None = Query(
        default=None,
        max_length=100
    ),
    active: bool | None = None,
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
    patients, total = crud.get_patients(
        db=db,
        q=q,
        active=active,
        page=page,
        page_size=page_size
    )

    return {
        "items": patients,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get(    
    "/{patient_id}",
    response_model=schemas.PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = crud.get_patient(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.patch(
    "/{patient_id}",
    response_model=schemas.PatientResponse
)
def update_patient(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db)
):
    patient = crud.update_patient(
        db,
        patient_id,
        patient_update
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.delete(
    "/{patient_id}",
    response_model=schemas.PatientResponse
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = crud.delete_patient(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.post(
    "/{patient_id}/restore",
    response_model=schemas.PatientResponse
)
def restore_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = patient_service.restore_patient(
        db,
        patient_id
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient