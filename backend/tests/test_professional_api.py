def test_create_and_get_professional(client):
    response = client.post(
        "/professionals/",
        json={
            "first_name": "Juan",
            "last_name": "Loccisano",
            "specialty": "Odontologia general",
            "license_number": "MN12345",
            "phone": "+54 9 11 2345 6789",
            "email": "juan@test.com"
        }
    )

    assert response.status_code == 201

    professional = response.json()

    assert professional["first_name"] == "Juan"
    assert professional["last_name"] == "Loccisano"

    professional_id = professional["id"]

    response = client.get(
        f"/professionals/{professional_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == professional_id


def test_duplicate_professional_returns_409(client):
    professional_data = {
        "first_name": "Maria",
        "last_name": "Gomez",
        "specialty": "Ortodoncia",
        "license_number": "MN99999",
        "phone": "+54 9 11 3456 7890",
        "email": "maria@test.com"
    }

    first_response = client.post(
        "/professionals/",
        json=professional_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/professionals/",
        json=professional_data
    )

    assert second_response.status_code == 409


def test_update_professional(client):
    create_response = client.post(
        "/professionals/",
        json={
            "first_name": "Pedro",
            "last_name": "Suarez",
            "specialty": "Odontologia general",
            "license_number": "MN54321",
            "phone": "+54 9 11 4567 8901",
            "email": "pedro@test.com"
        }
    )

    assert create_response.status_code == 201

    professional_id = create_response.json()["id"]

    update_response = client.patch(
        f"/professionals/{professional_id}",
        json={
            "specialty": "Endodoncia"
        }
    )

    assert update_response.status_code == 200
    assert update_response.json()["specialty"] == "Endodoncia"
    assert update_response.json()["first_name"] == "Pedro"


def test_soft_delete_and_restore_professional(client):
    create_response = client.post(
        "/professionals/",
        json={
            "first_name": "Lucia",
            "last_name": "Fernandez",
            "specialty": "Periodoncia",
            "license_number": "MN77777",
            "phone": "+54 9 11 5678 9012",
            "email": "lucia.prof@test.com"
        }
    )

    assert create_response.status_code == 201

    professional_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/professionals/{professional_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_at"] is not None

    get_response = client.get(
        f"/professionals/{professional_id}"
    )

    assert get_response.status_code == 404

    restore_response = client.post(
        f"/professionals/{professional_id}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["deleted_at"] is None

    get_response = client.get(
        f"/professionals/{professional_id}"
    )

    assert get_response.status_code == 200


def test_professional_search_and_pagination(client):
    professionals = [
        {
            "first_name": "Carlos",
            "last_name": "Perez",
            "specialty": "Ortodoncia",
            "license_number": "MN10001",
            "phone": "+54 9 11 6111 1111",
            "email": "carlos.prof@test.com"
        },
        {
            "first_name": "Ana",
            "last_name": "Lopez",
            "specialty": "Endodoncia",
            "license_number": "MN10002",
            "phone": "+54 9 11 6222 2222",
            "email": "ana.prof@test.com"
        },
        {
            "first_name": "Carolina",
            "last_name": "Diaz",
            "specialty": "Ortodoncia",
            "license_number": "MN10003",
            "phone": "+54 9 11 6333 3333",
            "email": "carolina.prof@test.com"
        }
    ]

    for professional in professionals:
        response = client.post(
            "/professionals/",
            json=professional
        )

        assert response.status_code == 201

    response = client.get(
        "/professionals/",
        params={
            "specialty": "Ortodoncia",
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