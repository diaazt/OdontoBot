from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
from auth_dependencies import require_roles
from database import get_db
from services import auth as auth_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=201
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin")
    )
):
    try:
        return auth_service.create_user(
            db,
            user
        )

    except auth_service.UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )