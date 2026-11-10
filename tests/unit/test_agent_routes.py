from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.assistant import get_client
from app.auth import get_current_user
from app.database import get_db
from app.main import app


def test_agent_chat_requires_auth():
    r = TestClient(app).post("/agent/chat", json={"message": "hi"})
    assert r.status_code in (401, 403)


def test_agent_resume_requires_auth():
    r = TestClient(app).post("/agent/resume", json={"thread_id": "x", "approved": True})
    assert r.status_code in (401, 403)


def test_resume_unknown_thread_is_404():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1)
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_client] = lambda: None
    try:
        r = TestClient(app).post("/agent/resume", json={"thread_id": "nope", "approved": True})
        assert r.status_code == 404
    finally:
        app.dependency_overrides.clear()