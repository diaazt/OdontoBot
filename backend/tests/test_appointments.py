import models


def create_patient(db, number: int = 1, active: bool = True):
    patient = models.Patient(
        first_name=f"Patient{number}",
        last_name="Test",
        phone=f"+54911123456{number:02d}",
        active=active
    )

    db.add(patient)
    db.flush()

    return patient


def create_professional(
    db,
    number: int = 1,
    active: bool = True
):
    professional = models.Professional(
        first_name=f"Professional{number}",
        last_name="Test",
        active=active
    )

    db.add(professional)
    db.flush()

    return professional


def appointment_payload(
    patient_id: int,
    professional_id: int,
    start_at: str = "2026-10-20T15:00:00-03:00",
    end_at: str = "2026-10-20T16:00:00-03:00"
):
    return {
        "patient_id": patient_id,
        "professional_id": professional_id,
        "service_id": None,
        "start_at": start_at,
        "end_at": end_at,
        "reason": "Consulta",
        "notes": None
    }


def test_create_appointment(client, db):
    patient = create_patient(db)
    professional = create_professional(db)

    response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient.id,
            professional.id
        )
    )

    assert response.status_code == 201

    data = response.json()

    assert data["patient_id"] == patient.id
    assert data["professional_id"] == professional.id
    assert data["status"] == "scheduled"


def test_reject_overlapping_appointment(client, db):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)
    professional = create_professional(db)

    first_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional.id
        )
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional.id,
            start_at="2026-10-20T15:30:00-03:00",
            end_at="2026-10-20T16:30:00-03:00"
        )
    )

    assert second_response.status_code == 409


def test_allow_consecutive_appointments(client, db):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)
    professional = create_professional(db)

    first_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional.id
        )
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional.id,
            start_at="2026-10-20T16:00:00-03:00",
            end_at="2026-10-20T17:00:00-03:00"
        )
    )

    assert second_response.status_code == 201


def test_cancelled_appointment_does_not_block_slot(
    client,
    db
):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)
    professional = create_professional(db)

    first_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional.id
        )
    )

    assert first_response.status_code == 201

    appointment_id = first_response.json()["id"]

    cancel_response = client.patch(
        f"/appointments/{appointment_id}",
        json={
            "status": "cancelled"
        }
    )

    assert cancel_response.status_code == 200

    second_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional.id
        )
    )

    assert second_response.status_code == 201


def test_invalid_period_returns_422(client, db):
    patient = create_patient(db)
    professional = create_professional(db)

    response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient.id,
            professional.id,
            start_at="2026-10-20T16:00:00-03:00",
            end_at="2026-10-20T15:00:00-03:00"
        )
    )

    assert response.status_code == 422


def test_inactive_professional_cannot_receive_appointment(
    client,
    db
):
    patient = create_patient(db)
    professional = create_professional(
        db,
        active=False
    )

    response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient.id,
            professional.id
        )
    )

    assert response.status_code == 409


def test_update_cannot_create_overlap(client, db):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)
    professional = create_professional(db)

    first_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional.id,
            start_at="2026-10-20T15:00:00-03:00",
            end_at="2026-10-20T16:00:00-03:00"
        )
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional.id,
            start_at="2026-10-20T16:00:00-03:00",
            end_at="2026-10-20T17:00:00-03:00"
        )
    )

    assert second_response.status_code == 201

    second_id = second_response.json()["id"]

    update_response = client.patch(
        f"/appointments/{second_id}",
        json={
            "start_at": "2026-10-20T15:30:00-03:00"
        }
    )

    assert update_response.status_code == 409


def test_restore_rejects_overlap(client, db):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)
    professional = create_professional(db)

    first_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional.id
        )
    )

    assert first_response.status_code == 201

    first_id = first_response.json()["id"]

    delete_response = client.delete(
        f"/appointments/{first_id}"
    )

    assert delete_response.status_code == 200

    second_response = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional.id
        )
    )

    assert second_response.status_code == 201

    restore_response = client.post(
        f"/appointments/{first_id}/restore"
    )

    assert restore_response.status_code == 409


def test_filter_appointments_by_professional(
    client,
    db
):
    patient_1 = create_patient(db, 1)
    patient_2 = create_patient(db, 2)

    professional_1 = create_professional(db, 1)
    professional_2 = create_professional(db, 2)

    response_1 = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_1.id,
            professional_1.id
        )
    )

    response_2 = client.post(
        "/appointments/",
        json=appointment_payload(
            patient_2.id,
            professional_2.id
        )
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    response = client.get(
        "/appointments/",
        params={
            "professional_id": professional_1.id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert (
        data["items"][0]["professional_id"]
        == professional_1.id
    )                                                                                                                                                                                                                                               