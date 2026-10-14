import models

from security import hash_password


def create_user(
    db,
    email: str,
    password: str,
    role: str = "admin",
    active: bool = True
):
    user = models.User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        active=active
    )

    db.add(user)
    db.flush()

    return user


def login(
    client,
    email: str,
    password: str
):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )


def test_login_returns_access_token(client, db):
    create_user(
        db,
        email="admin@test.com",
        password="Password123!",
        role="admin"
    )

    response = login(
        client,
        "admin@test.com",
        "Password123!"
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_rejects_invalid_password(client, db):
    create_user(
        db,
        email="admin@test.com",
        password="Password123!"
    )

    response = login(
        client,
        "admin@test.com",
        "Incorrect123!"
    )

    assert response.status_code == 401


def test_auth_me_requires_token(client):
    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401


def test_auth_me_returns_current_user(client, db):
    user = create_user(
        db,
        email="admin@test.com",
        password="Password123!",
        role="admin"
    )

    login_response = login(
        client,
        user.email,
        "Password123!"
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["role"] == "admin"


def test_admin_can_create_user(client, db):
    admin = create_user(
        db,
        email="admin@test.com",
        password="Password123!",
        role="admin"
    )

    login_response = login(
        client,
        admin.email,
        "Password123!"
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "email": "secretary@test.com",
            "password": "Secretary123!",
            "role": "secretary"
        }
    )

    assert response.status_code == 201
    assert response.json()["role"] == "secretary"


def test_secretary_cannot_create_user(client, db):
    secretary = create_user(
        db,
        email="secretary@test.com",
        password="Password123!",
        role="secretary"
    )

    login_response = login(
        client,
        secretary.email,
        "Password123!"
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "email": "another@test.com",
            "password": "Password123!",
            "role": "professional"
        }
    )

    assert response.status_code == 403