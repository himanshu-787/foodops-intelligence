import re
from pathlib import Path

import pytest
from prometheus_client import generate_latest

yaml = pytest.importorskip("yaml")  # pyyaml na ho toh ye file skip hogi

ROOT = Path(__file__).resolve().parents[2]
ALERTS = ROOT / "monitoring" / "alerts.yml"
RUNBOOK = ROOT / "docs" / "runbook.md"


def rules():
    data = yaml.safe_load(ALERTS.read_text(encoding="utf-8"))
    return [r for g in data["groups"] for r in g["rules"]]


def test_every_alert_has_expr_severity_and_summary():
    assert rules(), "koi rule nahi mila"
    for r in rules():
        assert r["expr"].strip(), r["alert"]
        assert r["labels"]["severity"] in {"page", "ticket"}, r["alert"]
        assert r["annotations"]["summary"], r["alert"]


def test_alert_metric_names_exist_in_code():
    import app.main  # noqa: F401  (saari metrics register ho jaati hain)

    exposed = generate_latest().decode()
    for r in rules():
        for name in re.findall(r"foodops_[a-z_]+", r["expr"]):
            base = re.sub(r"_(bucket|count|sum)$", "", name)
            assert base in exposed, f"{r['alert']}: code mein ye metric nahi hai: {name}"


def test_runbook_has_a_section_for_every_alert():
    text = RUNBOOK.read_text(encoding="utf-8")
    for r in rules():
        assert f"## {r['alert']}" in text, r["alert"]
