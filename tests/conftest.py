import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # Har test ke liye naya khaali in-memory DB
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client):
    creds = {"email": "test@example.com", "password": "password123"}
    client.post("/auth/register", json=creds)
    res = client.post(
        "/auth/login",
        data={"username": creds["email"], "password": creds["password"]},
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def make_item(client, name="Dosa", price=80, stock=3):
    res = client.post("/menu", json={"name": name, "price": price, "stock": stock})
    return res.json()["id"]