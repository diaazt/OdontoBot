from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import schemas
from database import get_db
from services import professionals as professional_service


router = APIRouter(
    prefix="/professionals",
    tags=["Professionals"]
)

@router.post(
    "/",
    response_model=schemas.ProfessionalResponse,
    status_code=201
)
def create_professional(
    professional: schemas.ProfessionalCreate,
    db: Session = Depends(get_db)
):
    try:
        return professional_service.create_professional(
            db,
            professional
        )

    except professional_service.ProfessionalDuplicateError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except professional_service.ProfessionalArchivedError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "PROFESSIONAL_ARCHIVED",
                "message": "A matching archived professional already exists.",
                "professional_id": exc.professional_id
            }
        )


@router.get(
    "/",
    response_model=schemas.ProfessionalListResponse
)
def get_professionals(
    q: str | None = Query(
        default=None,
        max_length=100
    ),
    active: bool | None = None,
    specialty: str | None = Query(
        default=None,
        max_length=100
    ),
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
    professionals, total = professional_service.get_professionals(
        db=db,
        q=q,
        active=active,
        specialty=specialty,
        page=page,
        page_size=page_size
    )

    return {
        "items": professionals,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get(
    "/{professional_id}",
    response_model=schemas.ProfessionalResponse
)
def get_professional(
    professional_id: int,
    db: Session = Depends(get_db)
):
    professional = professional_service.get_professional(
        db,
        professional_id
    )

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return professional


@router.patch(
    "/{professional_id}",
    response_model=schemas.ProfessionalResponse
)
def update_professional(
    professional_id: int,
    professional_update: schemas.ProfessionalUpdate,
    db: Session = Depends(get_db)
):
    professional = professional_service.update_professional(
        db,
        professional_id,
        professional_update
    )

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return professional


@router.delete(
    "/{professional_id}",
    response_model=schemas.ProfessionalResponse
)
def delete_professional(
    professional_id: int,
    db: Session = Depends(get_db)
):
    professional = professional_service.delete_professional(
        db,
        professional_id
    )

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return professional

@router.post(
    "/{professional_id}/restore",
    response_model=schemas.ProfessionalResponse
)
def restore_professional(
    professional_id: int,
    db: Session = Depends(get_db)
):
    professional = professional_service.restore_professional(
        db,
        professional_id
    )

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return professional