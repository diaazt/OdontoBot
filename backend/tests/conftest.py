import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

import models
from config import settings
from database import Base, get_db
from main import app


TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database="odontobot_test",
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()