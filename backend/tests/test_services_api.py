def test_create_service_with_initial_price(client):
    response = client.post(
        "/services/",
        json={
            "name": "Limpieza",
            "description": "Limpieza dental completa",
            "estimated_duration_minutes": 45,
            "initial_price": 50000
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Limpieza"
    assert data["estimated_duration_minutes"] == 45

    assert len(data["prices"]) == 1
    assert data["prices"][0]["amount"] == "50000.00"
    assert data["prices"][0]["valid_until"] is None


def test_duplicate_service_returns_409(client):
    service_data = {
        "name": "Consulta",
        "description": "Consulta general",
        "estimated_duration_minutes": 30,
        "initial_price": 30000
    }

    first_response = client.post(
        "/services/",
        json=service_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/services/",
        json=service_data
    )

    assert second_response.status_code == 409


def test_change_service_price_preserves_history(client):
    create_response = client.post(
        "/services/",
        json={
            "name": "Conducto",
            "description": "Tratamiento de conducto",
            "estimated_duration_minutes": 90,
            "initial_price": 80000
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    price_response = client.post(
        f"/services/{service_id}/prices",
        json={
            "amount": 95000
        }
    )

    assert price_response.status_code == 200

    data = price_response.json()

    assert len(data["prices"]) == 2

    old_price = next(
        price
        for price in data["prices"]
        if price["amount"] == "80000.00"
    )

    current_price = next(
        price
        for price in data["prices"]
        if price["amount"] == "95000.00"
    )

    assert old_price["valid_until"] is not None
    assert current_price["valid_until"] is None

    assert old_price["valid_until"] == current_price["valid_from"]


def test_same_service_price_returns_409(client):
    create_response = client.post(
        "/services/",
        json={
            "name": "Extraccion",
            "description": "Extraccion dental",
            "estimated_duration_minutes": 60,
            "initial_price": 70000
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    response = client.post(
        f"/services/{service_id}/prices",
        json={
            "amount": 70000
        }
    )

    assert response.status_code == 409


def test_update_service(client):
    create_response = client.post(
        "/services/",
        json={
            "name": "Blanqueamiento",
            "description": "Blanqueamiento dental",
            "estimated_duration_minutes": 60,
            "initial_price": 100000
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    update_response = client.patch(
        f"/services/{service_id}",
        json={
            "estimated_duration_minutes": 75,
            "description": "Blanqueamiento dental completo"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["estimated_duration_minutes"] == 75
    assert data["description"] == "Blanqueamiento dental completo"

    # El precio no debería cambiar por modificar el Service.
    assert len(data["prices"]) == 1
    assert data["prices"][0]["amount"] == "100000.00"


def test_soft_delete_and_restore_service(client):
    create_response = client.post(
        "/services/",
        json={
            "name": "Radiografia",
            "description": "Radiografia dental",
            "estimated_duration_minutes": 20,
            "initial_price": 20000
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/services/{service_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_at"] is not None

    get_response = client.get(
        f"/services/{service_id}"
    )

    assert get_response.status_code == 404

    restore_response = client.post(
        f"/services/{service_id}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["deleted_at"] is None

    get_response = client.get(
        f"/services/{service_id}"
    )

    assert get_response.status_code == 200


def test_archived_duplicate_service_returns_409(client):
    service_data = {
        "name": "Implante",
        "description": "Implante dental",
        "estimated_duration_minutes": 120,
        "initial_price": 400000
    }

    create_response = client.post(
        "/services/",
        json=service_data
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/services/{service_id}"
    )

    assert delete_response.status_code == 200

    duplicate_response = client.post(
        "/services/",
        json=service_data
    )

    assert duplicate_response.status_code == 409

    detail = duplicate_response.json()["detail"]

    assert detail["code"] == "SERVICE_ARCHIVED"
    assert detail["service_id"] == service_id


def test_invalid_service_data_returns_422(client):
    response = client.post(
        "/services/",
        json={
            "name": "",
            "description": "Dato invalido",
            "estimated_duration_minutes": -10,
            "initial_price": -5000
        }
    )

    assert response.status_code == 422

def test_service_search_and_pagination(client):
    services = [
        {
            "name": "Consulta",
            "description": "Consulta odontologica general",
            "estimated_duration_minutes": 30,
            "initial_price": 30000
        },
        {
            "name": "Extraccion",
            "description": "Extraccion dental",
            "estimated_duration_minutes": 60,
            "initial_price": 70000
        },
        {
            "name": "Limpieza",
            "description": "Limpieza dental completa",
            "estimated_duration_minutes": 45,
            "initial_price": 50000
        }
    ]

    for service in services:
        response = client.post(
            "/services/",
            json=service
        )

        assert response.status_code == 201

    response = client.get(
        "/services/",
        params={
            "page": 1,
            "page_size": 2
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2

    search_response = client.get(
        "/services/",
        params={
            "q": "limp"
        }
    )

    assert search_response.status_code == 200

    search_data = search_response.json()

    assert search_data["total"] == 1
    assert len(search_data["items"]) == 1
    assert search_data["items"][0]["name"] == "Limpieza"