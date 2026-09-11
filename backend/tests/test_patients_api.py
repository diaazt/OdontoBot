def test_create_and_get_patient(client):
    response = client.post(
        "/patients/",
        json={
            "first_name": "Carlos",
            "last_name": "Perez",
            "phone": "+54 9 11 2345 6789",
            "email": "carlos@test.com"
        }
    )

    assert response.status_code == 201

    patient = response.json()

    assert patient["first_name"] == "Carlos"
    assert patient["last_name"] == "Perez"

    patient_id = patient["id"]

    response = client.get(
        f"/patients/{patient_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == patient_id

def test_duplicate_patient_returns_409(client):
    patient_data = {
        "first_name": "Carlos",
        "last_name": "Perez",
        "phone": "+54 9 11 2345 6789",
        "email": "carlos@test.com"
    }

    first_response = client.post(
        "/patients/",
        json=patient_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/patients/",
        json=patient_data
    )

    assert second_response.status_code == 409


def test_update_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "first_name": "Ana",
            "last_name": "Gomez",
            "phone": "+54 9 11 3456 7890",
            "email": "ana@test.com"
        }
    )

    patient_id = create_response.json()["id"]

    update_response = client.patch(
        f"/patients/{patient_id}",
        json={
            "first_name": "Analia"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Analia"
    assert update_response.json()["last_name"] == "Gomez"


def test_soft_delete_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "first_name": "Pedro",
            "last_name": "Lopez",
            "phone": "+54 9 11 4567 8901",
            "email": "pedro@test.com"
        }
    )

    patient_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/patients/{patient_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_at"] is not None

    get_response = client.get(
        f"/patients/{patient_id}"
    )

    assert get_response.status_code == 404


def test_restore_patient(client):
    create_response = client.post(
        "/patients/",
        json={
            "first_name": "Lucia",
            "last_name": "Fernandez",
            "phone": "+54 9 11 5678 9012",
            "email": "lucia@test.com"
        }
    )

    patient_id = create_response.json()["id"]

    client.delete(
        f"/patients/{patient_id}"
    )

    restore_response = client.post(
        f"/patients/{patient_id}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["deleted_at"] is None

    get_response = client.get(
        f"/patients/{patient_id}"
    )

    assert get_response.status_code == 200

def test_list_patients_with_search_and_pagination(client):
    patients = [
        {
            "first_name": "Carlos",
            "last_name": "Perez",
            "phone": "+54 9 11 1111 1111",
            "email": "carlos.pagination@test.com"
        },
        {
            "first_name": "Lucia",
            "last_name": "Gomez",
            "phone": "+54 9 11 2222 2222",
            "email": "lucia.pagination@test.com"
        },
        {
            "first_name": "Carolina",
            "last_name": "Lopez",
            "phone": "+54 9 11 3333 3333",
            "email": "carolina.pagination@test.com"
        }
    ]

    for patient in patients:
        response = client.post("/patients/", json=patient)
        assert response.status_code == 201

    response = client.get(
        "/patients/",
        params={
            "q": "car",
            "page": 1,
            "page_size": 1
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) == 1

def test_archived_duplicate_returns_409(client):
    patient_data = {
        "first_name": "Martin",
        "last_name": "Suarez",
        "phone": "+54 9 11 4444 4444",
        "email": "martin.archived@test.com"
    }

    create_response = client.post(
        "/patients/",
        json=patient_data
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/patients/{patient_id}"
    )

    assert delete_response.status_code == 200

    recreate_response = client.post(
        "/patients/",
        json=patient_data
    )

    assert recreate_response.status_code == 409

    detail = recreate_response.json()["detail"]

    assert detail["code"] == "PATIENT_ARCHIVED"
    assert detail["patient_id"] == patient_id