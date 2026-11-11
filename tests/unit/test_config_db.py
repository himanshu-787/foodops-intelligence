from app.config import database_url, is_sqlite, normalize_db_url


def test_normalize_heroku_style_url():
    assert normalize_db_url("postgres://u:p@h:5432/db") == "postgresql+psycopg://u:p@h:5432/db"


def test_normalize_plain_postgresql_and_idempotent():
    out = normalize_db_url("postgresql://u:p@h/db")
    assert out == "postgresql+psycopg://u:p@h/db"
    assert normalize_db_url(out) == out  # dobara normalize karne se na bigde


def test_sqlite_untouched_and_default(monkeypatch):
    assert normalize_db_url("sqlite:///./x.db") == "sqlite:///./x.db"
    assert is_sqlite("sqlite:///./x.db") and not is_sqlite("postgresql+psycopg://h/db")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database_url() == "sqlite:///./foodops.db"
