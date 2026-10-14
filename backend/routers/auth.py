from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
from auth_dependencies import get_current_user
from database import get_db
from security import create_access_token
from services import auth as auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        user = auth_service.authenticate_user(
            db,
            login_data
        )

    except auth_service.InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc)
        )

    except auth_service.InactiveUserError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user