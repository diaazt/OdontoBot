import models


def create_professional(
    db,
    number: int = 1,
    active: bool = True
):
    professional = models.Professional(
        first_name=f"Professional{number}",
        last_name="Availability",
        active=active
    )

    db.add(professional)
    db.flush()

    return professional


def create_patient(db, number: int = 1):
    patient = models.Patient(
        first_name=f"Patient{number}",
        last_name="Availability",
        phone=f"+54911123478{number:02d}",
        active=True
    )

    db.add(patient)
    db.flush()

    return patient


def test_create_working_hours(client, db):
    professional = create_professional(db)

    response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "13:00:00",
            "active": True
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["professional_id"] == professional.id
    assert data["weekday"] == 0
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "13:00:00"


def test_reject_overlapping_working_hours(client, db):
    professional = create_professional(db)

    first_response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "13:00:00"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "12:00:00",
            "end_time": "16:00:00"
        }
    )

    assert second_response.status_code == 409


def test_allow_consecutive_working_hours(client, db):
    professional = create_professional(db)

    first_response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "13:00:00"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "13:00:00",
            "end_time": "17:00:00"
        }
    )

    assert second_response.status_code == 201


def test_time_off_cannot_overlap_appointment(client, db):
    professional = create_professional(db)
    patient = create_patient(db)

    appointment_response = client.post(
        "/appointments/",
        json={
            "patient_id": patient.id,
            "professional_id": professional.id,
            "service_id": None,
            "start_at": "2026-10-19T10:00:00-03:00",
            "end_at": "2026-10-19T11:00:00-03:00",
            "reason": "Consulta"
        }
    )

    assert appointment_response.status_code == 201

    response = client.post(
        f"/availability/professionals/{professional.id}/time-off",
        json={
            "start_at": "2026-10-19T10:30:00-03:00",
            "end_at": "2026-10-19T12:00:00-03:00",
            "reason": "Personal"
        }
    )

    assert response.status_code == 409


def test_available_slots_exclude_appointments_and_time_off(
    client,
    db
):
    professional = create_professional(db)
    patient = create_patient(db)

    working_hours_response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "13:00:00"
        }
    )

    assert working_hours_response.status_code == 201

    appointment_response = client.post(
        "/appointments/",
        json={
            "patient_id": patient.id,
            "professional_id": professional.id,
            "service_id": None,
            "start_at": "2026-10-19T10:00:00-03:00",
            "end_at": "2026-10-19T11:00:00-03:00"
        }
    )

    assert appointment_response.status_code == 201

    time_off_response = client.post(
        f"/availability/professionals/{professional.id}/time-off",
        json={
            "start_at": "2026-10-19T12:00:00-03:00",
            "end_at": "2026-10-19T12:30:00-03:00",
            "reason": "Personal"
        }
    )

    assert time_off_response.status_code == 201

    response = client.get(
        f"/availability/professionals/{professional.id}/slots",
        params={
            "target_date": "2026-10-19",
            "duration_minutes": 60,
            "slot_step_minutes": 30
        }
    )

    assert response.status_code == 200

    data = response.json()

    starts = [
        slot["start_at"]
        for slot in data["slots"]
    ]

    assert starts == [
        "2026-10-19T09:00:00-03:00",
        "2026-10-19T11:00:00-03:00"
    ]


def test_no_working_hours_returns_no_slots(client, db):
    professional = create_professional(db)

    response = client.get(
        f"/availability/professionals/{professional.id}/slots",
        params={
            "target_date": "2026-10-19",
            "duration_minutes": 60
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["slots"] == []


def test_inactive_professional_cannot_have_working_hours(
    client,
    db
):
    professional = create_professional(
        db,
        active=False
    )

    response = client.post(
        f"/availability/professionals/{professional.id}/working-hours",
        json={
            "weekday": 0,
            "start_time": "09:00:00",
            "end_time": "13:00:00"
        }
    )

    assert response.status_code == 409