from fastapi.testclient import TestClient

from app.main import app


def test_ask_requires_auth():
    r = TestClient(app).post("/rag/ask", json={"question": "refund kab milega"})
    assert r.status_code in (401, 403)