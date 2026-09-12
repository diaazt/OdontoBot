from sqlalchemy.orm import Session
from datetime import datetime, timezone
import crud
import schemas

class ServiceDuplicateError(Exception):
    pass


class ServiceArchivedError(Exception):
    def __init__(self, service_id: int):
        self.service_id = service_id

        super().__init__(
            f"An archived service with id {service_id} "
            "matches this service."
        )

class ServicePriceNotFoundError(Exception):
    pass


class ServicePriceUnchangedError(Exception):
    pass

def create_service(
    db: Session,
    service: schemas.ServiceCreate
):
    duplicate = crud.find_duplicate_service(
        db,
        service
    )

    if duplicate is not None:
        raise ServiceDuplicateError(
            "A service with this name already exists."
        )

    archived = crud.find_archived_duplicate_service(
        db,
        service
    )

    if archived is not None:
        raise ServiceArchivedError(
            archived.id
        )

    try:
        db_service = crud.create_service(
            db,
            service
        )

        crud.create_service_price(
            db=db,
            service_id=db_service.id,
            amount=service.initial_price
        )

        db.commit()

        db.refresh(db_service)

        return crud.get_service(
            db,
            db_service.id
        )

    except Exception:
        db.rollback()
        raise

def get_service(
    db: Session,
    service_id: int
):
    return crud.get_service(
        db,
        service_id
    )


def get_services(
    db: Session,
    q: str | None = None,
    active: bool | None = None,
    page: int = 1,
    page_size: int = 20
):
    return crud.get_services(
        db=db,
        q=q,
        active=active,
        page=page,
        page_size=page_size
    )


def update_service(
    db: Session,
    service_id: int,
    service: schemas.ServiceUpdate
):
    return crud.update_service(
        db,
        service_id,
        service
    )


def delete_service(
    db: Session,
    service_id: int
):
    return crud.delete_service(
        db,
        service_id
    )


def restore_service(
    db: Session,
    service_id: int
):
    return crud.restore_service(
        db,
        service_id
    )

def change_service_price(
    db: Session,
    service_id: int,
    new_price: schemas.ServicePriceCreate
):
    try:
        # Bloqueamos el servicio durante la operación.
        db_service = crud.get_service_for_update(
            db,
            service_id
        )

        if db_service is None:
            return None

        current_price = crud.get_current_service_price(
            db,
            service_id
        )

        if current_price is None:
            raise ServicePriceNotFoundError(
                "The service has no current price."
            )

        if current_price.amount == new_price.amount:
            raise ServicePriceUnchangedError(
                "The new price is the same as the current price."
            )

        now = datetime.now(timezone.utc)

        crud.close_service_price(
            db=db,
            price=current_price,
            valid_until=now
        )

        crud.create_service_price(
            db=db,
            service_id=service_id,
            amount=new_price.amount,
            valid_from=now
        )

        db.commit()

        return crud.get_service(
            db,
            service_id
        )

    except (
        ServicePriceNotFoundError,
        ServicePriceUnchangedError
    ):
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise