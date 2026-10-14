from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select

import models
import schemas
from database import SessionLocal
from services import auth as auth_service


def main():
    db = SessionLocal()

    try:
        existing_admin = db.scalar(
            select(models.User)
            .where(models.User.role == "admin")
            .limit(1)
        )

        if existing_admin is not None:
            print("An admin user already exists. Bootstrap aborted.")
            return

        email = input("Admin email: ").strip().lower()

        password = getpass("Admin password: ")
        password_confirmation = getpass(
            "Confirm admin password: "
        )

        if password != password_confirmation:
            print("Passwords do not match.")
            return

        user_data = schemas.UserCreate(
            email=email,
            password=password,
            role="admin"
        )

        user = auth_service.create_user(
            db,
            user_data
        )

        print(
            f"Admin created successfully: "
            f"{user.email} (id={user.id})"
        )

    except ValidationError as exc:
        print("Invalid user data:")
        print(exc)

    except auth_service.UserAlreadyExistsError as exc:
        print(str(exc))

    finally:
        db.close()


if __name__ == "__main__":
    main()