import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import database_url, is_sqlite

load_dotenv()

URL = database_url()
DATABASE_URL = URL

engine = create_engine(
    URL,
    connect_args={"check_same_thread": False} if is_sqlite(URL) else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Har request ko ek session do, khatam hone par band karo."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
