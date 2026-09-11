from sqlalchemy.orm import Session

import crud
import models
import schemas


def create_professional(
    db: Session,
    professional: schemas.ProfessionalCreate
) -> models.Professional:

    duplicate = crud.find_duplicate_professional(
        db,
        professional
    )

    if duplicate is not None:
        raise ProfessionalDuplicateError(
            "A matching professional already exists."
        )

    archived = crud.find_archived_duplicate_professional(
        db,
        professional
    )

    if archived is not None:
        raise ProfessionalArchivedError(
            archived.id
        )

    return crud.create_professional(
        db,
        professional
    )


def get_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    return crud.get_professional(
        db,
        professional_id
    )


def get_professionals(
    db: Session,
    q: str | None = None,
    active: bool | None = None,
    specialty: str | None = None,
    page: int = 1,
    page_size: int = 20
):
    return crud.get_professionals(
        db=db,
        q=q,
        active=active,
        specialty=specialty,
        page=page,
        page_size=page_size
    )


def update_professional(
    db: Session,
    professional_id: int,
    professional_update: schemas.ProfessionalUpdate
) -> models.Professional | None:

    return crud.update_professional(
        db,
        professional_id,
        professional_update
    )


def delete_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    return crud.delete_professional(
        db,
        professional_id
    )

class ProfessionalDuplicateError(Exception):
    pass


class ProfessionalArchivedError(Exception):
    def __init__(self, professional_id: int):
        self.professional_id = professional_id

        super().__init__(
            f"An archived professional with id "
            f"{professional_id} matches this professional."
        )

def restore_professional(
    db: Session,
    professional_id: int
) -> models.Professional | None:

    return crud.restore_professional(
        db,
        professional_id
    )