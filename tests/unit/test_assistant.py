from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import assistant, models
from app.database import Base
from app.main import app


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def make_order(db, user_id, status="placed"):
    import uuid

    o = models.Order(
        user_id=user_id,
        status=status,
        idempotency_key=str(uuid.uuid4()),
        total=100.0,
    )
    db.add(o)
    db.commit()
    return o


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.messages = self

    def create(self, **kwargs):
        return self.responses.pop(0)


def test_tool_returns_own_order(db):
    o = make_order(db, user_id=1)
    reg = assistant.build_tools(db, SimpleNamespace(id=1))
    out, err = assistant.run_tool(reg, "get_order_status", {"order_id": o.id})
    assert not err and "placed" in out


def test_tool_hides_other_users_order(db):
    o = make_order(db, user_id=2)  # order user 2 ka hai
    reg = assistant.build_tools(db, SimpleNamespace(id=1))  # login user 1 hai
    out, _ = assistant.run_tool(reg, "get_order_status", {"order_id": o.id})
    assert "not found" in out and "placed" not in out


def test_loop_uses_tool_and_reports_it(db):
    o = make_order(db, user_id=1)
    tool_use = SimpleNamespace(
        type="tool_use", id="t1", name="get_order_status", input={"order_id": o.id}
    )
    client = FakeClient([
        SimpleNamespace(stop_reason="tool_use", content=[tool_use]),
        SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="Placed hai")]),
    ])
    reply, used = assistant.run_assistant("x", db, SimpleNamespace(id=1), client)
    assert reply == "Placed hai" and used == ["get_order_status"]


def test_endpoint_requires_auth():
    r = TestClient(app).post("/assistant/chat", json={"message": "hi"})
    assert r.status_code in (401, 403)


def test_rate_limit_blocks_11th_call():
    assistant._hits.clear()
    for _ in range(assistant.RATE_LIMIT):
        assistant.check_rate_limit(99)
    with pytest.raises(HTTPException) as e:
        assistant.check_rate_limit(99)
    assert e.value.status_code == 429