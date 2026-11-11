import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")  # container mein .env nahi hota, theek hai


def cors_origins() -> list[str]:
    """Comma-separated env var se list. Default: local Vite dev server."""
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


DEFAULT_DB_URL = "sqlite:///./foodops.db"


def is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def normalize_db_url(url: str) -> str:
    """Platforms 'postgres://' dete hain; SQLAlchemy ko driver wala form chahiye."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def database_url() -> str:
    return normalize_db_url(os.getenv("DATABASE_URL", DEFAULT_DB_URL))
