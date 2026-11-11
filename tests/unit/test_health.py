from fastapi.testclient import TestClient

from app.config import cors_origins
from app.database import get_db
from app.main import app


def test_health_ok():
    r = TestClient(app).get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_ready_ok_with_working_db(db):
    app.dependency_overrides[get_db] = lambda: db
    try:
        r = TestClient(app).get("/ready")
        assert r.status_code == 200 and r.json()["status"] == "ready"
    finally:
        app.dependency_overrides.clear()


def test_ready_503_when_db_down():
    class Broken:
        def execute(self, *a, **k):
            raise RuntimeError("db down")

    app.dependency_overrides[get_db] = lambda: Broken()
    try:
        assert TestClient(app).get("/ready").status_code == 503
    finally:
        app.dependency_overrides.clear()


def test_cors_origins_parsing(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://a.com, https://b.com ,")
    assert cors_origins() == ["https://a.com", "https://b.com"]
    monkeypatch.delenv("CORS_ORIGINS")
    assert cors_origins() == ["http://localhost:5173"]
