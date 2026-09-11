from sqlalchemy.orm import Session

import crud
import models
import schemas


class PatientDuplicateError(Exception):
    pass

class PatientArchivedError(Exception):
    def __init__(self, patient_id: int):
        self.patient_id = patient_id
        super().__init__(
            f"An archived patient with id {patient_id} matches this patient."
        )

def create_patient(
    db: Session,
    patient: schemas.PatientCreate
) -> models.Patient:

    duplicate = crud.find_duplicate_patient(db, patient)

    if duplicate is not None:
        raise PatientDuplicateError(
            "A patient with the same name and contact information already exists."
        )

    archived = crud.find_archived_duplicate_patient(db, patient)

    if archived is not None:
        raise PatientArchivedError(archived.id)

    return crud.create_patient(db, patient)

def restore_patient(
    db: Session,
    patient_id: int
) -> models.Patient | None:

    return crud.restore_patient(db, patient_id)