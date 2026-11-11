from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_requirements_has_no_windows_only_packages():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8", errors="ignore").lower()
    assert "pywin32" not in text


def test_dockerignore_keeps_secrets_and_db_out():
    lines = (ROOT / ".dockerignore").read_text().split()
    assert ".env" in lines and "*.db" in lines
