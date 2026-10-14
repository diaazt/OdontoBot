from sqlalchemy.orm import Session

import crud
import schemas
from security import hash_password, verify_password

class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass

def create_user(
    db: Session,
    user: schemas.UserCreate
):
    existing_user = crud.get_user_by_email(
        db,
        str(user.email)
    )

    if existing_user is not None:
        raise UserAlreadyExistsError(
            "A user with this email already exists."
        )

    hashed_password = hash_password(
        user.password
    )

    try:
        db_user = crud.create_user(
            db=db,
            email=str(user.email),
            password_hash=hashed_password,
            role=user.role
        )

        db.commit()
        db.refresh(db_user)

        return db_user

    except Exception:
        db.rollback()
        raise

def authenticate_user(
    db: Session,
    login: schemas.LoginRequest
):
    user = crud.get_user_by_email(
        db,
        str(login.email)
    )

    if user is None:
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not verify_password(
        login.password,
        user.password_hash
    ):
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not user.active:
        raise InactiveUserError(
            "User account is inactive."
        )

    return user