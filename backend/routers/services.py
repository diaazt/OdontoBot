from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import schemas
from database import get_db
from services import catalog as service_catalog


router = APIRouter(
    prefix="/services",
    tags=["Services"]
)


@router.post(
    "/",
    response_model=schemas.ServiceResponse,
    status_code=201
)
def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    try:
        return service_catalog.create_service(
            db,
            service
        )

    except service_catalog.ServiceDuplicateError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except service_catalog.ServiceArchivedError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SERVICE_ARCHIVED",
                "message": "A matching archived service already exists.",
                "service_id": exc.service_id
            }
        )


@router.get(
    "/",
    response_model=schemas.ServiceListResponse
)
def get_services(
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
    services, total = service_catalog.get_services(
        db=db,
        q=q,
        active=active,
        page=page,
        page_size=page_size
    )

    return {
        "items": services,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get(
    "/{service_id}",
    response_model=schemas.ServiceResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = service_catalog.get_service(
        db,
        service_id
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.patch(
    "/{service_id}",
    response_model=schemas.ServiceResponse
)
def update_service(
    service_id: int,
    service: schemas.ServiceUpdate,
    db: Session = Depends(get_db)
):
    updated_service = service_catalog.update_service(
        db,
        service_id,
        service
    )

    if updated_service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return updated_service


@router.delete(
    "/{service_id}",
    response_model=schemas.ServiceResponse
)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = service_catalog.delete_service(
        db,
        service_id
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.post(
    "/{service_id}/restore",
    response_model=schemas.ServiceResponse
)
def restore_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = service_catalog.restore_service(
        db,
        service_id
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.post(
    "/{service_id}/prices",
    response_model=schemas.ServiceResponse
)
def change_service_price(
    service_id: int,
    price: schemas.ServicePriceCreate,
    db: Session = Depends(get_db)
):
    try:
        service = service_catalog.change_service_price(
            db=db,
            service_id=service_id,
            new_price=price
        )

        if service is None:
            raise HTTPException(
                status_code=404,
                detail="Service not found"
            )

        return service

    except service_catalog.ServicePriceNotFoundError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except service_catalog.ServicePriceUnchangedError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )