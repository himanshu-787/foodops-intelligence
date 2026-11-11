import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def order_factory(db):
    _counter = [0]

    def _create(user_id=1, status="placed"):
        _counter[0] += 1
        o = models.Order(
            user_id=user_id,
            status=status,
            idempotency_key=f"order-key-{user_id}-{_counter[0]}",
            total=100.0,
        )
        db.add(o)
        db.commit()
        db.refresh(o)
        return o

    return _create
